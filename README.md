Nash is stand alone note as HTML.

=======
# naMD: Note as Markdown

naMD (Note as Markdown) is a simple, standalone note-taking application packaged entirely within a single HTML file. It requires no backend server, database, or special software beyond a modern web browser.

Inspired by the idea of creating useful tools within a single HTML file, naMD provides a basic WYSIWYG editor for creating notes with rich text formatting, with the added ability to export your notes directly as Markdown.

## Features

* **Standalone Operation:** Works completely offline once the `namd.html` file is saved.
* **WYSIWYG Editor:** Provides basic formatting options:
    * Text size (XL, L, M, S)
    * Bold, Italic, Underline
    * Links
    * Image insertion (embeds images as Base64 data URIs)
    * Text color
    * Highlight color
* **Saving Options:**
    * **Save/Share as HTML:** Saves the entire note, including the editor interface, as a self-contained, editable `.html` file (legacy Nash format).
    * **Save/Share as Read-Only HTML:** Saves the note content as an `.html` file but disables the editing interface.
    * **Save as Markdown:** Converts the current note content (from HTML) into Markdown format and downloads it as a `.md` file, ideal for use with Git or other Markdown tools.
* **Light/Dark Mode:** Adapts basic colors based on system preferences.

## How to Use

1.  Download the `namd.html` file.
2.  Open it in your web browser.
3.  Write your title and note content using the editor toolbar.
4.  Use the **Save icon (💾)** dropdown menu to choose your desired save format:
    * Save a fully editable HTML version locally.
    * Save a read-only HTML version locally.
    * Save the content as a Markdown (`.md`) file locally.
5.  The saved `.html` files can be opened directly in a browser. The saved `.md` files are plain text Markdown.

**Note on Markdown:** While you can save *as* Markdown, the editor itself visually works with HTML. Loading `.md` files back into the editor for editing would require further modification (adding a Markdown-to-HTML library and file loading logic).

## GitHub Integration

There is no built-in feature to save directly to GitHub repositories.

To save your notes to a Git repository (like GitHub):

1.  Use the "Save as Markdown" option to download the `.md` file to your local machine.
2.  Copy or move the downloaded `.md` file into your local Git repository folder.
3.  Use standard Git commands (`git add`, `git commit`, `git push`) or a Git client to add the file and push it to your remote repository.

## Source

This project is based on the original Nash project. Feel free to modify and use it.
Find the original source code at: [https://github.com/keepworking/nash](https://github.com/keepworking/nash) (Note: Link points to the original Nash repo)
