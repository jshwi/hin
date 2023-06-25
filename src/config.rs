use std::{
    env,
    path::{Path, PathBuf},
};

use color_eyre::Result;
use ini::Ini;
use log::debug;

use crate::DOTFILES;


pub struct Config {
    pub path: PathBuf,
    pub ini: Ini,
}


impl Config {
    pub fn new() -> Result<Self> {
        let dotfiles = &env::var(DOTFILES)?;
        let dotfiles = Path::new(dotfiles);
        let path = Path::new(dotfiles).join("dotfiles.ini");
        debug!("config = {}", path.display());
        let mut ini = Ini::new();
        if path.is_file() {
            ini = Ini::load_from_file(&path).unwrap();
        }
        Ok(Self { ini, path })
    }

    pub fn add(&mut self, key: &String, value: &String) {
        self.ini.with_section(None::<String>).set(key, value);
        self.ini.write_to_file(&self.path).unwrap();
    }
}
