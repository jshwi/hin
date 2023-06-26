use std::{env, path::Path};

use color_eyre::Result;
use git2::Repository;

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
    println!("cloning '{}' into {}", repo_name, path.display());
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
