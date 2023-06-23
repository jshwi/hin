use std::{env, fs::remove_file, path::Path};

use color_eyre::Result;
use git2::Repository;
use ini::Ini;
use log::debug;

use crate::DOTFILES;

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


pub fn commit(file: String) -> Result<()> {
    todo!("commit {}", file);
}


pub fn push() -> Result<()> {
    todo!("push");
}


pub fn remove(file: String) -> Result<()> {
    todo!("remove {}", file);
}


pub fn status() -> Result<()> {
    todo!("status");
}


pub fn undo() -> Result<()> {
    todo!("undo");
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
