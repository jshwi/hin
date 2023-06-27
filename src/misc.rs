use std::{env, fs, path::Path};

use color_eyre::Result;
use git2::Oid;
use log::debug;

use crate::DOTFILES;

pub fn set_repo_path() -> Result<()> {
    let name: String = env::var("CARGO_PKG_NAME")?;
    debug!("CARGO_PKG_NAME={}", name);
    let repo = env::var(DOTFILES);
    let base_dirs = directories::BaseDirs::new().unwrap();
    let user_data_dir = base_dirs.data_dir();
    env::set_var("USER_DATA_DIR", user_data_dir);
    let default = user_data_dir.join(name);
    if repo.is_err() {
        debug!("DOTFILES not set, defaulting to {}", default.display());
        env::set_var(DOTFILES, default)
    } else {
        debug!("DOTFILES={}", repo.unwrap());
    };
    let dotfiles = env::var(DOTFILES)?;
    if !Path::new(&dotfiles).exists() {
        if fs::create_dir_all(&dotfiles).is_ok() {};
        debug!("creating {}", dotfiles);
    }
    Ok(())
}


fn find_last_commit(repo: &git2::Repository) -> Result<git2::Commit> {
    let obj = repo.head()?.resolve()?.peel(git2::ObjectType::Commit)?;
    Ok(obj
        .into_commit()
        .map_err(|_| git2::Error::from_str("Couldn't find commit"))?)
}


pub fn commit(path: &Path, message: &str) -> Result<Oid> {
    // todo
    //   proper author, email, and time
    let repo = git2::Repository::open(env::var(DOTFILES)?)?;
    let mut index = repo.index()?;
    index.add_path(path)?;
    let oid = index.write_tree()?;
    let signature = git2::Signature::now("author", "author@email")?;
    let parent_commit = find_last_commit(&repo)?;
    let tree = repo.find_tree(oid)?;
    Ok(repo.commit(
        Some("HEAD"),
        &signature,
        &signature,
        message,
        &tree,
        &[&parent_commit],
    )?)
}
