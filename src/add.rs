use std::{
    env,
    fs::rename,
    path::{Path, PathBuf},
};

use color_eyre::Result;
use ini::Ini;
use log::debug;
use regex::Regex;
use relative_path::RelativePath;

use crate::{gitignore::unignore, misc::is_child_of, DOTFILES};

fn add_dir(p0: &Path) {
    todo!("add dir {:?}", p0)
}


fn child_from(p0: &str, p1: &str) -> PathBuf {
    todo!("{}.child({})", p1, p0)
}


pub fn add(file: String) -> Result<()> {
    let mut entry = PathBuf::from(&file);
    let dotfiles = &env::var(DOTFILES)?;
    let dotfiles = Path::new(dotfiles);
    let dotfiles_ini = Path::new(dotfiles).join("dotfiles.ini");
    debug!("listing dotfiles configured in {:?}", dotfiles_ini);
    let mut config = Ini::load_from_file(&dotfiles_ini).unwrap();
    let dotfile_name = Regex::new(r"^\.")
        .unwrap()
        .replace(entry.file_name().unwrap().to_str().unwrap(), "")
        .to_string();
    let home_file = format!("$HOME/{}", file);
    let dotfile_repr_file = format!("${}/{}", DOTFILES, dotfile_name);
    for (_, prop) in &config {
        debug!("checking if config contains {}", &home_file);
        if prop.contains_key(&home_file) {
            // todo
            //   make this an error
            panic!("{} already added", &home_file)
        }
    }
    debug!("config does not contain {}", home_file);
    if entry.is_symlink() {
        entry = entry.read_link()?;
        if !entry.exists() {
            // todo
            //   make this an error
            panic!("{} is a dangling symlink", &file)
        }
    }
    let dotfile_path = entry.parent().unwrap().join(&dotfile_name);
    let dotfile_path = RelativePath::from_path(&dotfile_path)?;
    let mut dotfile_path = dotfile_path.to_logical_path(dotfiles);
    if dotfile_path.exists() {
        dotfile_path = dotfile_path.parent().unwrap().join(format!(
            "{:?}.{:?}",
            &dotfile_name,
            chrono::Utc::now().timestamp()
        ));
    }
    debug!("moving {:?} to {:?}", &entry, dotfile_path);
    match rename(&entry, dotfile_path) {
        Ok(_) => {
            if entry.is_dir() {
                // add .gitignore files and check for any children that
                // might already be versioned
                add_dir(&entry)
            }
            config
                .with_section(None::<String>)
                .set(home_file, dotfile_repr_file);
            config.write_to_file(&dotfiles_ini)?;
        }
        Err(e) => {
            let mut add_child = false;
            for (_, prop) in &config {
                for (key, value) in prop.iter() {
                    if is_child_of(&file, Path::new(key), Path::new(value)) {
                        let child = child_from(&file, value);
                        unignore(
                            &child,
                            &PathBuf::from(child.parent().unwrap()),
                        );
                        add_child = true;
                        break;
                    }
                }
            }
            if !add_child {
                // todo
                //   make this an error
                panic!("{}: {} not found", e, &file)
            }
        }
    }
    println!("added {:?}", entry);
    // todo
    //  commit here
    Ok(())
}
