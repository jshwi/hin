use std::{env, fs::rename, os::unix::fs::symlink, path::Path};

use color_eyre::Result;
use git2::Repository;
use ini::Ini;

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
    println!("added {}", file);
    Ok(())
}


pub fn commit(file: String) -> Result<()> {
    println!("committed {}", file);
    Ok(())
}


pub fn install() -> Result<()> {
    let dotfiles = &env::var(DOTFILES)?;
    let path = Path::new(dotfiles).join("dotfiles.ini");
    let config = Ini::load_from_file(path).unwrap();
    for (_, prop) in &config {
        for (key, value) in prop.iter() {
            let key_path = shellexpand::env(&key)?.to_string();
            let value_path = shellexpand::env(&value)?.to_string();
            let key_path = Path::new(&key_path);
            if key_path.exists()
                && !key_path.is_symlink()
                && key_path.read_link()? == Path::new(&value_path)
            {
                println!(
                    "{} {:?}",
                    ansi_term::Color::Yellow.bold().paint("backed up"),
                    key_path
                );
                rename(
                    key_path,
                    Path::new(&key_path.parent().unwrap()).join(format!(
                        "{:?}.{}",
                        key_path.file_name(),
                        chrono::Utc::now().timestamp()
                    )),
                )?;
            };
            // TODO
            // while true
            // if file exists, unlink
            // if file not found, mkdir
            symlink(&value_path, key_path)?;
        }
    }
    Ok(())
}


pub fn link(symlink: String, target: String) -> Result<()> {
    println!("linked {} to {}", symlink, target);
    Ok(())
}


pub fn push() -> Result<()> {
    println!("pushed");
    Ok(())
}


pub fn remove(file: String) -> Result<()> {
    println!("removed {}", file);
    Ok(())
}


pub fn status() -> Result<()> {
    println!("showed status");
    Ok(())
}


pub fn undo() -> Result<()> {
    println!("undone");
    Ok(())
}


pub fn uninstall() -> Result<()> {
    println!("uninstalled");
    Ok(())
}
