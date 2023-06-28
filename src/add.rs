use std::{fs, path::PathBuf};

use color_eyre::Result;
use log::debug;

use crate::{
    config::Config,
    files::{FileTrait, Matrix},
    git::Git,
    gitignore::{unignore, Gitignore},
};

pub fn add(file: String, mut config: Config, git: Git) -> Result<()> {
    let mut entry = Matrix::new(
        &file,
        &PathBuf::from(&file)
            .file_name()
            .unwrap()
            .to_os_string()
            .into_string()
            .unwrap(),
    );
    for (_, prop) in &config.ini {
        debug!("checking if config contains {}", &entry.key.repr());
        if prop.contains_key(&entry.key.repr()) {
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
    let mut remove_from = false;
    match fs::rename(&entry.key.path(), &entry.value.path()) {
        Ok(_) => {
            if entry.key.path().is_dir() {
                // add .gitignore files and check for any children that
                // might already be versioned
                let gitignore = Gitignore::new(&entry.value.path());
                gitignore.make();
                for (_, prop) in &config.ini {
                    for (key, value) in prop.iter() {
                        let existing =
                            Matrix::new(&key.to_string(), &value.to_string());
                        if existing.is_child_of(&entry)
                            && existing.value.repr().starts_with("$DOTFILES")
                        {
                            // move the child back under the new dotfile
                            // and remove from config
                            let child = entry.child(&existing);
                            fs::rename(child.key.path(), child.value.path())
                                .unwrap();
                            remove_from = true;
                            println!(
                                "unlinked {}",
                                existing.key.path().display()
                            );
                            println!(
                                "committing {}",
                                existing.key.path().display()
                            );
                            // ensure the child remains versioned by
                            // including it in all .gitignore files back
                            // up to the parent
                            unignore(&child.value.path(), &entry.value.path());
                        }
                    }
                }
            }
            if remove_from {
                config.remove(
                    &entry.key.path().into_os_string().into_string().unwrap(),
                );
            }
            config.add(&entry.key.repr(), &entry.value.repr());
            debug!(
                "added {}: {} to config",
                &entry.key.repr(),
                &entry.value.repr()
            );
        }
        Err(e) => {
            let mut add_child = false;
            for (_, prop) in &config.ini {
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
                panic!("{}", e)
            }
        }
    }
    git.add(vec![
        "dotfiles.ini".to_string(),
        entry.value.relpath().into_os_string().into_string().unwrap(),
    ])?;
    git.commit(&format!("add {}", entry.key.relpath().display()))?;
    println!("added {}", &entry.key.path().display());
    Ok(())
}
