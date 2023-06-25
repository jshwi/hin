use std::{
    env,
    fs,
    path::{Path, PathBuf},
};

use color_eyre::Result;
use ini::Ini;
use log::debug;

use crate::{
    files::{FileTrait, Matrix},
    gitignore::unignore,
    DOTFILES,
};

fn add_dir(p0: &Path) {
    todo!("add dir {:?}", p0)
}


pub fn add(file: String) -> Result<()> {
    let mut entry = Matrix::new(
        &file,
        &PathBuf::from(&file)
            .file_name()
            .unwrap()
            .to_os_string()
            .into_string()
            .unwrap(),
    );
    let dotfiles = &env::var(DOTFILES)?;
    let dotfiles = Path::new(dotfiles);
    let dotfiles_ini = Path::new(dotfiles).join("dotfiles.ini");
    debug!("listing dotfiles configured in {}", dotfiles_ini.display());
    let mut config = Ini::new();
    if dotfiles_ini.is_file() {
        config = Ini::load_from_file(&dotfiles_ini).unwrap();
    }
    for (_, prop) in &config {
        debug!("checking if config contains {}", &entry.key.repr());
        if prop.contains_key(&entry.key.repr()) {
            // todo
            //   make this an error
            panic!("{} already added", &entry.key.repr())
        }
    }
    debug!("config does not contain {}", &entry.key.repr());
    if entry.key.path().is_symlink() {
        entry = entry.linksrc()?
    }
    if entry.value.path().exists() {
        entry = entry.timestamped()
    }
    debug!(
        "moving {} to {}",
        &entry.key.path().display(),
        &entry.value.path().display()
    );
    match fs::rename(&entry.key.path(), &entry.value.path()) {
        Ok(_) => {
            if entry.key.path().is_dir() {
                // add .gitignore files and check for any children that
                // might already be versioned
                add_dir(&entry.key.path())
            }
            config
                .with_section(None::<String>)
                .set(&entry.key.repr(), &entry.value.repr());
            config.write_to_file(&dotfiles_ini)?;
            debug!(
                "added {}: {} to config",
                &entry.key.repr(),
                &entry.value.repr()
            );
        }
        Err(e) => {
            let mut add_child = false;
            for (_, prop) in &config {
                for (key, value) in prop.iter() {
                    let existing =
                        Matrix::new(&String::from(key), &String::from(value));
                    if entry.is_child_of(&existing) {
                        let child = existing.child(&entry);
                        unignore(&child.value.path(), &entry.value.path());
                        add_child = true;
                        break;
                    }
                }
            }
            if !add_child {
                // todo
                //   make this an error
                panic!("{}", e)
            }
        }
    }
    println!("added {:?}", &entry.key.path());
    // todo
    //  commit here
    Ok(())
}
