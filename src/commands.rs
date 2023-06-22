use std::{env, path::Path};

use color_eyre::Result;
use git2::Repository;
use ini::Ini;

pub fn clone(url: &str) -> Result<()> {
    let dotfiles = &env::var("DOTFILES")?;
    let path = Path::new(&dotfiles);
    let repo_name = url
        .split('/')
        .collect::<Vec<&str>>()
        .pop()
        .unwrap()
        .replace(".git", "");
    println!("cloning '{}' into {:?}", repo_name, path);
    match Repository::clone(url, path) {
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
