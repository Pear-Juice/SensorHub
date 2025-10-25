{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
    # nativeBuildInputs is usually what you want -- tools you need to run
    nativeBuildInputs = with pkgs.buildPackages; [
    python3
    python313Packages.pandas
    python313Packages.matplotlib
    python313Packages.numpy
    python313Packages.regex
  ];
}

