# exocad2STL
This repo contains the source code to convert exocad-generated HTML pages to STL.

The exocad HTML page contains 3D meshes in [OpenCTM](https://github.com/Danny02/OpenCTM) format in a JS variable, embedded in a `<script>`tag.

This utils parses the HTML file, process it looking at the `<script>` elements, and looks for the matching expression.

The data is `base64`-encoded. The script decodes it first and then looks at the bytes structure for 3D model data. Typically, multiple 3D meshes are embedded in a single JS variable.

The CTM data is then processed by `OpenCTM` libraries using Python bindings, and the resulting vertices-faces information is encapsulated in a `trimesh` object. The object can be further processed or simply exported to STL.

## Dependencies
The dependencies are listed in the `requirements.txt` file, to be installed via `pip install -r requirements.txt`.

Another dependency is the OpenCTM libraries, which is listed as a `git` submodule, and needs to be installed by following the instruction in `openctm/COMPILING.txt`. The libraries also need to be installed to be properly found by `ctypes`.

## Telegram bot
The code also contains a Telegram application to allow a bot to perform the conversion. See [`python-telegram-bot`](https://python-telegram-bot.org) for information on how the Python wrappers for Telegram bots are implemented. 

The current bot downloads the HTML file, extracts the data, converts all the CTM meshes to STL, and sends the files in a compressed `.zip` folder.

## Author
[Gianfranco Di Domenico](https://github.com/gian-didom). 
The author takes no responsibility for unproper usage of this codebase, especially if such usage violates any of exocad Terms and Conditions. All the operations work on non-proprietary file formats and specifications.

The code is provided as-is, and the author does not guarantee its correctness or fitness for any particular purpose. 