use std::{borrow::Cow, env};

fn _context(s: &str) -> Result<Option<Cow<'static, str>>, env::VarError> {
    match env::var(s) {
        Ok(value) => Ok(Some(value.into())),
        Err(env::VarError::NotPresent) => Ok(Some("".into())),
        Err(e) => Err(e),
    }
}


trait FileABC {
    fn name(&self) -> String;
    fn env(&self) -> String;
    fn root(&self) -> String;
    fn relpath(&self) -> String {
        self.name().replace(&self.root(), "")
    }
    fn path(&self) -> String {
        format!("{}/{}", self.root(), self.relpath())
    }
}


impl Symlink {
    fn _new(name: String) -> Symlink {
        Symlink {
            name: shellexpand::env_with_context(&name, _context)
                .unwrap()
                .to_string(),
        }
    }
}


struct Symlink {
    name: String,
}


impl FileABC for Symlink {
    fn name(&self) -> String {
        format!(
            "{:?}/{}",
            home::home_dir(),
            shellexpand::env_with_context(&self.name, _context).unwrap()
        )
    }

    fn env(&self) -> String {
        "HOME".to_string()
    }

    fn root(&self) -> String {
        env::var(self.env()).unwrap()
    }
}
