use std::{
    env,
    fs,
    path::{Path, PathBuf},
};

use color_eyre::Result;
use git2::Oid;
use log::debug;

use crate::{files::FileTrait, DOTFILES};

pub fn set_repo_path() -> Result<PathBuf> {
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
    let dotfiles = PathBuf::from(&dotfiles);
    if !dotfiles.exists() {
        if fs::create_dir_all(&dotfiles).is_ok() {};
        debug!("creating {}", dotfiles.display());
    }
    Ok(dotfiles)
}


fn find_last_commit(repo: &git2::Repository) -> Result<git2::Commit> {
    let obj = repo.head()?.resolve()?.peel(git2::ObjectType::Commit)?;
    Ok(obj
        .into_commit()
        .map_err(|_| git2::Error::from_str("Couldn't find commit"))?)
}


fn add_to_index(
    path: &Path,
    relpath: &Path,
    index: &mut git2::Index,
) -> Result<()> {
    if path.is_dir() {
        debug!("getting files from {}", path.display());
        let paths = fs::read_dir(path)?;
        for p in paths {
            let p = p.unwrap().path();
            debug!("{}", p.display());
            let relpath = PathBuf::from(
                p.into_os_string()
                    .into_string()
                    .unwrap()
                    .replace(&format!("{}/", env::var(DOTFILES)?), ""),
            );
            debug!("adding {} to index", relpath.display());
            index.add_path(&relpath)?;
        }
    } else {
        index.add_path(relpath)?;
    }
    index.add_path(Path::new("dotfiles.ini"))?;
    Ok(())
}


pub fn commit_matrix(
    repository: &git2::Repository,
    path: &impl FileTrait,
    message: &str,
) -> Result<Oid> {
    // todo
    //   proper author, email, and time
    let mut index = repository.index()?;
    add_to_index(&path.path(), &path.relpath(), &mut index)?;
    let oid = index.write_tree()?;
    let signature = git2::Signature::now("author", "author@email")?;
    let parent_commit = find_last_commit(repository)?;
    let tree = repository.find_tree(oid)?;
    Ok(repository.commit(
        Some("HEAD"),
        &signature,
        &signature,
        message,
        &tree,
        &[&parent_commit],
    )?)
}


pub fn create_initial_commit(
    repository: &git2::Repository,
    path: &Path,
) -> Result<Oid> {
    let sig = repository.signature()?;
    let tree_id = {
        let mut index = repository.index()?;
        add_to_index(path, Path::new(&path.file_name().unwrap()), &mut index)?;
        index.write_tree()?
    };
    let tree = repository.find_tree(tree_id)?;
    Ok(repository.commit(
        Some("HEAD"),
        &sig,
        &sig,
        "Initial commit",
        &tree,
        &[],
    )?)
}
