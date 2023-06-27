use std::{
    env,
    fs,
    path::{Path, PathBuf},
};

use color_eyre::Result;
use log::debug;

use crate::{files::FileTrait, DOTFILES};


pub fn find_last_commit(
    repository: &git2::Repository,
) -> Result<git2::Commit> {
    let obj = repository.head()?.resolve()?.peel(git2::ObjectType::Commit)?;
    Ok(obj
        .into_commit()
        .map_err(|_| git2::Error::from_str("Couldn't find commit"))?)
}


pub fn add_to_index(
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
) -> Result<git2::Oid> {
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
) -> Result<git2::Oid> {
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
