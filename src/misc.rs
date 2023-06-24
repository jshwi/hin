use std::env;

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
    Ok(())
}
