use std::{
    env,
    path::{Component, PathBuf},
};

use color_eyre::Result;
use regex::Regex;

use crate::DOTFILES;


pub trait FileTrait {
    fn string(&self) -> &String;
    fn env(&self) -> &String;
    fn root(&self) -> PathBuf;
    fn relpath(&self) -> PathBuf {
        let str_root = &self.root().into_os_string().into_string().unwrap();
        PathBuf::from(
            self.string()
                .to_string()
                .replace(&format!("{}/", str_root), ""),
        )
    }
    fn path(&self) -> PathBuf {
        PathBuf::from(&self.root()).join(&self.relpath())
    }
    fn repr(&self) -> String {
        format!(
            "${}/{}",
            &self.env(),
            &self.relpath().into_os_string().into_string().unwrap()
        )
    }
}


pub struct Symlink {
    string: String,
    env: String,
}


impl Symlink {
    fn new(string: &String, env: String) -> Result<Self> {
        let string = home::home_dir()
            .unwrap()
            .join(shellexpand::env(&string)?.to_string())
            .into_os_string()
            .into_string()
            .unwrap();
        Ok(Self { string, env })
    }
}


impl FileTrait for Symlink {
    fn string(&self) -> &String {
        &self.string
    }

    fn env(&self) -> &String {
        &self.env
    }

    fn root(&self) -> PathBuf {
        PathBuf::from(env::var(&self.env).unwrap())
    }
}


pub struct Dotfile {
    string: String,
    env: String,
}


impl Dotfile {
    fn new(string: &String, env: String) -> Result<Self> {
        let string = shellexpand::env(&string)?.to_string();
        Ok(Self { string, env })
    }
}


impl FileTrait for Dotfile {
    fn string(&self) -> &String {
        &self.string
    }

    fn env(&self) -> &String {
        &self.env
    }

    fn root(&self) -> PathBuf {
        PathBuf::from(env::var(&self.env).unwrap())
    }

    fn relpath(&self) -> PathBuf {
        let relpath = PathBuf::from(
            self.string()
                .to_string()
                .replace(&format!("{:?}/", &self.root()), ""),
        );
        PathBuf::from(
            Regex::new(r"^\.")
                .unwrap()
                .replace(relpath.to_str().unwrap(), "")
                .to_string(),
        )
    }
}


pub struct Matrix {
    pub key: Symlink,
    pub value: Dotfile,
}


impl Matrix {
    pub fn new(key: &String, value: &String) -> Self {
        Self {
            key: Symlink::new(key, "HOME".to_string()).unwrap(),
            value: Dotfile::new(value, DOTFILES.to_string()).unwrap(),
        }
    }

    pub fn linksrc(&self) -> Result<Self> {
        let value = &self.key.path().read_link()?;
        if !value.exists() {
            // todo
            //   make this an error
            panic!("{:?} is a dangling symlink", &value)
        }
        let value = String::from(value.to_str().unwrap());
        Ok(Self::new(&value, &value))
    }

    pub fn timestamped(&self) -> Self {
        Self::new(
            self.key.string(),
            &self
                .value
                .path()
                .parent()
                .unwrap()
                .join(format!(
                    "{:?}.{:?}",
                    &self.value.string,
                    chrono::Utc::now().timestamp()
                ))
                .into_os_string()
                .into_string()
                .unwrap(),
        )
    }

    pub fn is_child_of(&self, other: &Matrix) -> bool {
        self.key.path().starts_with(other.key.path())
            || self.value.path().starts_with(other.key.path())
    }

    pub fn child(&self, entry: &Matrix) -> Matrix {
        let mut relpath = PathBuf::from(
            Regex::new(r"^\.")
                .unwrap()
                .replace(entry.key.relpath().to_str().unwrap(), "")
                .to_string(),
        );
        if relpath.components().count() > 1 {
            let mut components: Vec<_> = relpath.components().collect();
            while components[0]
                != Component::Normal(self.value.path().file_name().unwrap())
            {
                components.pop();
            }
            relpath = components.iter().collect()
        }
        Self::new(
            &entry.value.path().into_os_string().into_string().unwrap(),
            &self
                .value
                .path()
                .parent()
                .unwrap()
                .join(relpath)
                .into_os_string()
                .into_string()
                .unwrap(),
        )
    }
}
