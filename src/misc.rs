use std::env;

use color_eyre::Result;
use log::debug;

use crate::DOTFILES;


pub fn set_repo_path() -> Result<()> {
    let name: String = env::var("CARGO_PKG_NAME")?;
    debug!("CARGO_PKG_NAME={}", name);
    let repo = env::var(DOTFILES);
    let default = directories::BaseDirs::new().unwrap().data_dir().join(name);
    if repo.is_err() {
        debug!("DOTFILES not set, defaulting to {:?}", default);
        env::set_var(DOTFILES, default)
    } else {
        debug!("DOTFILES={}", repo.unwrap());
    };
    Ok(())
}
