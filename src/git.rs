use std::{
    env,
    fs,
    path::{Path, PathBuf},
};

use color_eyre::Result;
use log::debug;

use crate::DOTFILES;

pub struct Git {
    repository: git2::Repository,
}


impl Git {
    pub fn new(dotfiles: &Path) -> Result<Git> {
        Ok(Self {
            repository: git2::Repository::init(dotfiles)?,
        })
    }

    pub fn find_last_commit(&self) -> Result<git2::Commit> {
        let obj = self
            .repository
            .head()?
            .resolve()?
            .peel(git2::ObjectType::Commit)?;
        Ok(obj
            .into_commit()
            .map_err(|_| git2::Error::from_str("Couldn't find commit"))?)
    }

    pub fn add_to_index(&self, path: Option<&Path>) -> Result<git2::Oid> {
        let mut index = self.repository.index()?;
        if let Some(p) = path {
            if p.is_dir() {
                debug!("getting files from {}", p.display());
                let paths = fs::read_dir(p)?;
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
                let relpath = PathBuf::from(
                    p.as_os_str()
                        .to_str()
                        .unwrap()
                        .replace(&format!("{}/", env::var(DOTFILES)?), ""),
                );
                index.add_path(&relpath)?;
            }
        }
        index.add_path(Path::new("dotfiles.ini"))?;
        Ok(index.write_tree()?)
    }

    pub fn commit_matrix(
        &self,
        path: Option<&Path>,
        message: &str,
    ) -> Result<git2::Oid> {
        // todo
        //   proper author, email, and time
        let signature = self.repository.signature()?;
        let oid = self.add_to_index(path)?;
        let parent_commit = self.find_last_commit()?;
        let tree = self.repository.find_tree(oid)?;
        Ok(self.repository.commit(
            Some("HEAD"),
            &signature,
            &signature,
            message,
            &tree,
            &[&parent_commit],
        )?)
    }

    pub fn create_initial_commit(&self) -> Result<git2::Oid> {
        let signature = self.repository.signature()?;
        let oid = self.add_to_index(None)?;
        let tree = self.repository.find_tree(oid)?;
        Ok(self.repository.commit(
            Some("HEAD"),
            &signature,
            &signature,
            "Initial commit",
            &tree,
            &[],
        )?)
    }
}
