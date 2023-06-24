use std::{
    env,
    fs::rename,
    path::{Path, PathBuf},
};

use color_eyre::Result;
use ini::Ini;
use log::debug;

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
    for (_, prop) in &config {
        if prop.contains_key(&file) {
            // todo
            //   make this an error
            panic!("{} already added", &file)
        }
    }
    if entry.is_symlink() {
        entry = entry.read_link()?;
        if !entry.exists() {
            // todo
            //   make this an error
            panic!("{} is a dangling symlink", &file)
        }
    }
    if entry.exists() {
        entry = entry.parent().unwrap().join(format!(
            "{:?}.{:?}",
            entry.file_name(),
            chrono::Utc::now().timestamp()
        ));
    }
    match rename(&entry, dotfiles.join(entry.file_name().unwrap())) {
        Ok(_) => {
            if entry.is_dir() {
                // add .gitignore files and check for any children that
                // might already be versioned
                add_dir(&entry)
            }
            // todo
            //   config.add(entry)
        }
        Err(_) => {
            if !add_child(&file, config) {
                // todo
                //   make this an error
                panic!("{} not found", &file)
            }
        }
    }
    println!("added {:?}", entry);
    // todo
    //  commit here
    Ok(())
}
