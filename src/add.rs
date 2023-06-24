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


fn add_child(p0: &str, config: Ini) -> bool {
    for (_, prop) in &config {
        for (key, value) in prop.iter() {
            if is_child_of(p0, Path::new(key), Path::new(value)) {
                let child = child_from(p0, value);
                unignore(&child, &PathBuf::from(child.parent().unwrap()));
                return true;
            }
        }
    }
    false
}

fn child_from(p0: &str, p1: &str) -> PathBuf {
    todo!("{}.child({})", p1, p0)
}


pub fn add(file: String) -> Result<()> {
    let mut entry = PathBuf::from(&file);
    let dotfiles = &env::var(DOTFILES)?;
    let dotfiles = Path::new(dotfiles);
    let path = Path::new(dotfiles).join("dotfiles.ini");
    debug!("listing dotfiles configured in {:?}", path);
    let config = Ini::load_from_file(path).unwrap();
    let home_file = format!("$HOME/{}", file);
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
    // _re.sub(r"^\.", "", str(super().relpath))
    let dotfile_path = entry.parent().unwrap().join(
        Regex::new(r"^\.")
            .unwrap()
            .replace(entry.file_name().unwrap().to_str().unwrap(), "")
            .to_string(),
    );
    let dotfile_path = RelativePath::from_path(&dotfile_path)?;
    let mut dotfile_path = dotfile_path.to_logical_path(dotfiles);
    if dotfile_path.exists() {
        dotfile_path = dotfile_path.parent().unwrap().join(format!(
            "{:?}.{:?}",
            Regex::new(r"^\.")
                .unwrap()
                .replace(entry.file_name().unwrap().to_str().unwrap(), ""),
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
            // todo
            //   config.add(entry)
        }
        Err(e) => {
            if !add_child(&file, config) {
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
