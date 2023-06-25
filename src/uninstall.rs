use std::{fs, path::Path};

use crate::config::Config;

pub fn uninstall() -> color_eyre::Result<()> {
    let config = Config::new()?;
    for (_, prop) in &config.ini {
        for (key, _) in prop.iter() {
            let key_path = shellexpand::env(&key)?.to_string();
            let key_path = Path::new(&key_path);
            if key_path.is_symlink() {
                println!("\t{}", key_path.display());
                fs::remove_file(key_path)?;
            }
        }
    }
    Ok(())
}
