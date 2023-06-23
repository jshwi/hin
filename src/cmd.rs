use std::{env, path::Path};

use color_eyre::Result;
use git2::Repository;
use ini::Ini;


pub fn clone(url: String) -> Result<()> {
    let dotfiles = &env::var("DOTFILES")?;
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
    let dotfiles = &env::var("DOTFILES")?;
    let path = Path::new(dotfiles).join("dotfiles.ini");
    let config = Ini::load_from_file(path).unwrap();
    for (_, prop) in &config {
        for (key, value) in prop.iter() {
            let kind = ansi_term::Color::Green.bold().paint("+");
            println!("{} {:?}:{:?}", kind, key, value);
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
    println!("installed");
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
