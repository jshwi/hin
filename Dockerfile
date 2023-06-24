FROM rust:1.67 as rust-playground
ENV USER=root
ENV CARGO_TARGET_DIR=/opt/hin/target
ENV CFLAGS=-mno-outline-atomics
WORKDIR /root
COPY ./src /opt/hin/src
COPY ./Cargo.toml ./Cargo.lock /opt/hin/
RUN apt-get update && apt-get install xdg-user-dirs python3-pip exa -y
COPY <<'EOF' /opt/entrypoint
#!/bin/sh
rm -rf -- ..?* .[!.]* *
xdg-user-dirs-update
echo "alias 'ls=exa'" >> /root/.bashrc
for i in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25; do
  mkdir -p ".config/$i" && touch ".config/$i/file.txt"
  mkdir ".test${i}" && touch ".test${i}/file.txt"
done
mkdir .config/nvim && touch .config/nvim/init.lua
mkdir .vim && touch .vim/vimrc
mkdir -p .level1/level2/level3 && touch .level1/level2/level3/file.txt
mkdir -p .level2/level3/level4 && touch .level2/level3/level4/file.txt
mkdir .linkdir && touch .linkdir/linkfile && ln -s .linkdir/linkfile .link
touch .somerc
git config --global user.name "${USER}"
git config --global user.email "${USER}@localhost"
exec "$@"
EOF
COPY <<'EOF' /bin/rhin
#!/bin/sh
cargo run --manifest-path /opt/hin/Cargo.toml "$@"
EOF
COPY <<'EOF' /bin/c
#!/bin/sh
stdin="${1}"
if command -v pygmentize >/dev/null 2>&1; then
  if pygmentize --help >/dev/null 2>&1; then
    pygmentize -O style=monokai -f console256 -g "${stdin}"
    return 0
  fi
fi
cat "${stdin}"
EOF
RUN <<EOF
chmod 755 /opt/entrypoint
chmod 755 /bin/rhin
pip3 install hin pygments
cargo build --manifest-path /opt/hin/Cargo.toml
EOF
