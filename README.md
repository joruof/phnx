# phnx [fē-niks]

A low effort (but very useful) script for hot code reloading of python apps.
Piggybacks on ipython and watchdog to reload as much code as possible.

This is very useful for rapid prototyping or explorative development.

## Usage

```
./phnx.py module.main
```

This will import ```module``` and execute the function ```main```,
which is expected to run some sort of application loop (e.g. gui event loop).

If a file change is detected in the directory tree below the current working directory,
```module.main``` is terminated via SIGINT, changed modules are reloaded, and
```module.main``` is called again.
