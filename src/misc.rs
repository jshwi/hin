use std::{
    env,
    fs::create_dir_all,
    path::{Path, PathBuf},
};

use color_eyre::Result;
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
        debug!("DOTFILES not set, defaulting to {:?}", default);
        env::set_var(DOTFILES, default)
    } else {
        debug!("DOTFILES={}", repo.unwrap());
    };
    let dotfiles = env::var(DOTFILES)?;
    if !Path::new(&dotfiles).exists() {
        if create_dir_all(&dotfiles).is_ok() {};
        debug!("creating {}", dotfiles);
    }
    Ok(())
}


pub fn is_child_of(this: &str, other_key: &Path, other_value: &Path) -> bool {
    this.starts_with(other_key.to_str().unwrap())
        || this.starts_with(other_value.to_str().unwrap())
}


pub fn linksrc(entry: PathBuf) -> Result<PathBuf> {
    // value = _Path(_os.readlink(self.key.path))
    // if not value.exists():
    //     raise FileNotFoundError(f"{value.absolute()} is a dangling
    // symlink")
    //
    // return Entry.new(value)
    let entry = entry.read_link()?;
    if !entry.exists() {
        // todo
        //   make this an error
        panic!("{:?} is a dangling symlink", &entry)
    }
    Ok(entry)
}
