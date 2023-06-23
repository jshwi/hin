use std::{env, fs::remove_file, path::Path};

use ini::Ini;
use log::debug;

use crate::DOTFILES;

pub fn uninstall() -> color_eyre::Result<()> {
    let dotfiles = &env::var(DOTFILES)?;
    let path = Path::new(dotfiles).join("dotfiles.ini");
    debug!("installing dotfiles configured in {:?}", path);
    let config = Ini::load_from_file(path).unwrap();
    println!("removed the following dotfiles:");
    for (_, prop) in &config {
        for (key, _) in prop.iter() {
            let key_path = shellexpand::env(&key)?.to_string();
            let key_path = Path::new(&key_path);
            if key_path.is_symlink() {
                println!("\t{:?}", key_path);
                remove_file(key_path)?;
            }
        }
    }
    Ok(())
}
