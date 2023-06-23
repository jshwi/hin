use std::{
    env,
    fs::{create_dir, remove_file, rename},
    io::ErrorKind,
    os::unix::fs::symlink,
    path::Path,
};

use color_eyre::Result;
use git2::Repository;
use ini::Ini;
use log::debug;
use relative_path::RelativePath;

use crate::{gitignore::unignore, DOTFILES};

pub fn clone(url: String) -> Result<()> {
    let dotfiles = &env::var(DOTFILES)?;
    let path = Path::new(&dotfiles);
    let repo_name = url
        .split('/')
        .collect::<Vec<&str>>()
        .pop()
        .unwrap()
        .replace(".git", "");
    println!("cloning '{}' into {:?}", repo_name, path);
    match Repository::clone(&url, path) {
        Ok(repo) => repo,
        Err(e) => panic!("failed to clone: {}", e),
    };
    println!(
        "{}",
        ansi_term::Color::Green.bold().paint("cloned dotfile repo")
    );
    Ok(())
}


pub fn list() -> Result<()> {
    let dotfiles = &env::var(DOTFILES)?;
    let path = Path::new(dotfiles).join("dotfiles.ini");
    debug!("listing dotfiles configured in {:?}", path);
    let config = Ini::load_from_file(path).unwrap();
    for (_, prop) in &config {
        for (key, value) in prop.iter() {
            let mut kind = ansi_term::Color::Green.bold().paint("+");
            let mut path = key.to_string();
            if value.starts_with("$HOME") {
                kind = ansi_term::Color::Cyan.bold().paint("=");
                path += &format!(" -> {}", value);
            }
            println!("{} {}", kind, shellexpand::env(&path)?);
        }
    }
    Ok(())
}


pub fn add(file: String) -> Result<()> {
    debug!("added {}", file);
    Ok(())
}


pub fn commit(file: String) -> Result<()> {
    debug!("committed {}", file);
    Ok(())
}


pub fn install() -> Result<()> {
    let dotfiles = &env::var(DOTFILES)?;
    let path = Path::new(dotfiles).join("dotfiles.ini");
    debug!("installing dotfiles configured in {:?}", path);
    let config = Ini::load_from_file(path).unwrap();
    for (_, prop) in &config {
        for (key, value) in prop.iter() {
            let key_path = shellexpand::env(&key)?.to_string();
            let value_path = shellexpand::env(&value)?.to_string();
            let key_path = Path::new(&key_path);
            let value_path = Path::new(&value_path);
            let mut is_a_dotfiles_link = false;
            if key_path.is_symlink() {
                let linksrc = key_path.read_link()?;
                debug!("{:?} leads to {:?}", key_path, linksrc);
                debug!("value_path={:?}", value_path);
                if value_path == linksrc {
                    debug!("is a dotfiles link");
                    is_a_dotfiles_link = true;
                }
            }
            if key_path.exists() {
                if is_a_dotfiles_link {
                    debug!(
                        "removing {:?}, an existing dotfile link",
                        key_path
                    );
                    remove_file(key_path)?;
                } else {
                    let new_key_path = Path::new(&key_path.parent().unwrap())
                        .join(format!(
                            "{:?}.{}",
                            key_path.file_name(),
                            chrono::Utc::now().timestamp()
                        ));
                    debug!("renamed {:?} to {:?}", key_path, new_key_path);
                    rename(key_path, &new_key_path)?;
                    println!(
                        "{} {:?}",
                        ansi_term::Color::Yellow.bold().paint("backed up"),
                        key_path
                    )
                }
            }
            loop {
                match symlink(value_path, key_path) {
                    Ok(_) => {
                        println!(
                            "{} {:?}",
                            ansi_term::Color::Green.bold().paint("installed"),
                            key_path
                        );
                        break;
                    }
                    Err(error) => match error.kind() {
                        ErrorKind::AlreadyExists => {
                            debug!(
                                "removing {:?}, a dangling symlink",
                                key_path
                            );
                            remove_file(key_path)?;
                        }
                        ErrorKind::NotFound => {
                            let parent = key_path.parent().unwrap();
                            debug!("{:?} does not exist, creating", parent);
                            create_dir(parent)?
                        }
                        other_error => {
                            panic!(
                                "Problem installing file: {:?}",
                                other_error
                            );
                        }
                    },
                };
            }
        }
    }
    Ok(())
}


pub fn link(symlink: String, _target: String) -> Result<()> {
    let dotfiles = &env::var(DOTFILES)?;
    let path = Path::new(dotfiles).join("dotfiles.ini");
    debug!("dotfile configuration: {:?}", path);
    let mut config = Ini::load_from_file(path).unwrap();
    for (_, prop) in &mut config {
        // todo
        //  this only evaluates the string provided and not relative
        //  path, absolute path, etc.
        if prop.contains_key(&symlink) {
            // todo
            //  make this an error
            panic!("{} already added", &symlink)
        }
        for (key, value) in prop.iter() {
            let key_path = shellexpand::env(&key)?.to_string();
            let value_path = shellexpand::env(&value)?.to_string();
            let key_path = Path::new(&key_path);
            let value_path = Path::new(&value_path);
            let rel_new_path = RelativePath::new(&symlink);
            let rel_value_path =
                RelativePath::new(value_path.to_str().unwrap());
            let logical_path = rel_value_path.to_logical_path(dotfiles);
            if (symlink.starts_with(key_path.to_str().unwrap())
                || symlink.starts_with(value_path.to_str().unwrap()))
                && logical_path.exists()
            {
                debug!("{} starts with {:?}", symlink, key_path);
                debug!("or {} starts with {:?}", symlink, value_path);
                debug!("and {:?} exists", logical_path);
                unignore(
                    rel_new_path.to_logical_path(dotfiles),
                    rel_value_path.to_logical_path(dotfiles),
                );
            } else if rel_new_path != rel_value_path {
                debug!("{} not equal to {}", rel_new_path, rel_value_path);
                continue;
            }
            // todo
            //     config.add(custom)
            //     out.print(
            //         f"linked {custom.key.path} to "
            //         "{custom.value.path}"
            //     )
            //     return f"add {custom.key.path.name}"
        }
    }
    // todo
    //     raise ValueError(
    //         "link not related to a symlink or parent of a symlink"
    //         "in dotfile repo"
    //     )
    Ok(())
}


pub fn push() -> Result<()> {
    debug!("pushed");
    Ok(())
}


pub fn remove(file: String) -> Result<()> {
    debug!("removed {}", file);
    Ok(())
}


pub fn status() -> Result<()> {
    debug!("showed status");
    Ok(())
}


pub fn undo() -> Result<()> {
    debug!("undone");
    Ok(())
}


pub fn uninstall() -> Result<()> {
    let dotfiles = &env::var(DOTFILES)?;
    let path = Path::new(dotfiles).join("dotfiles.ini");
    debug!("installing dotfiles configured in {:?}", path);
    let config = Ini::load_from_file(path).unwrap();
    println!("removed the following dotfiles:");
    for (_, prop) in &config {
        for (key, _) in prop.iter() {
            let key_path = shellexpand::env(&key)?.to_string();
            let key_path = Path::new(&key_path);
            if key_path.is_symlink() {
                println!("\t{:?}", key_path);
                remove_file(key_path)?;
            }
        }
    }
    Ok(())
}
