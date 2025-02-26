from IPython.display import SVG
import subprocess
import tempfile
import os

def display_abc(abc_string):
    """
    Display ABC notation as SVG in a Jupyter notebook.
    Requires Node.js and the abcjs package to be installed.
    
    Parameters:
    -----------
    abc_string : str
        The ABC notation string to display
    
    Returns:
    --------
    IPython.display.SVG
        The rendered SVG of the music notation
    """
    # if abc string does not start with X: then add it
    if not abc_string.startswith('X:'):
        abc_string = 'X:1\n' + abc_string
    from IPython.display import SVG
import subprocess
import tempfile
import os

def display_abc(abc_string):
    """
    Convert ABC notation to SVG object for display in a Jupyter notebook.
    Requires Node.js and the abcjs package to be installed.
    
    Parameters:
    -----------
    abc_string : str
        The ABC notation string to convert
        
    Returns:
    --------
    IPython.display.SVG
        The SVG object containing the rendered music notation
    """
    # Create a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        # Write ABC to a temporary file
        abc_file = os.path.join(temp_dir, 'temp.abc')
        with open(abc_file, 'w') as f:
            f.write(abc_string)
        
        # Create a Node.js script to convert ABC to SVG
        node_script = os.path.join(temp_dir, 'convert.js')
        with open(node_script, 'w') as f:
            f.write("""
const fs = require('fs');
const { JSDOM } = require('jsdom');
const abcjs = require('abcjs');

// Create a DOM environment
const dom = new JSDOM('<!DOCTYPE html><div id="notation"></div>');
global.document = dom.window.document;
global.window = dom.window;

const abc = fs.readFileSync('temp.abc', 'utf-8');
const svg = abcjs.renderAbc('notation', abc, {
    responsive: 'resize',
    staffwidth: 740,
    scale: 1.2,
    format: {
        paddingright: 0,
        paddingleft: 0
    }
})[0];

// Get the generated SVG
const svgElement = document.getElementById('notation').innerHTML;
fs.writeFileSync('output.svg', svgElement);
""".replace('temp.abc', abc_file))
        
        try:
            # Install required packages
            subprocess.run(['npm', 'install', 'abcjs', 'jsdom'], 
                         cwd=temp_dir, 
                         check=True, 
                         capture_output=True)
            
            subprocess.run(['node', node_script], 
                         cwd=temp_dir, 
                         check=True, 
                         capture_output=True)
            
            # Read the generated SVG
            with open(os.path.join(temp_dir, 'output.svg'), 'r') as f:
                svg_content = f.read()
                
            # Return the SVG object
            return SVG(svg_content)
            
        except subprocess.CalledProcessError as e:
            print("Error converting ABC to SVG:")
            print(e.stderr.decode())
            return None
    # Create a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        # Write ABC to a temporary file
        abc_file = os.path.join(temp_dir, 'temp.abc')
        with open(abc_file, 'w') as f:
            f.write(abc_string)
        
        # Create a Node.js script to convert ABC to SVG
        node_script = os.path.join(temp_dir, 'convert.js')
        with open(node_script, 'w') as f:
            f.write("""
const fs = require('fs');
const { JSDOM } = require('jsdom');
const abcjs = require('abcjs');

// Create a DOM environment
const dom = new JSDOM('<!DOCTYPE html><div id="notation"></div>');
global.document = dom.window.document;
global.window = dom.window;

const abc = fs.readFileSync('temp.abc', 'utf-8');
const svg = abcjs.renderAbc('notation', abc, {
    responsive: 'resize',
    staffwidth: 740,
    scale: 1.2,
    format: {
        paddingright: 0,
        paddingleft: 0
    }
})[0];

// Get the generated SVG
const svgElement = document.getElementById('notation').innerHTML;
fs.writeFileSync('output.svg', svgElement);
""".replace('temp.abc', abc_file))
        
        try:
            # Install required packages
            subprocess.run(['npm', 'install', 'abcjs', 'jsdom'], 
                         cwd=temp_dir, 
                         check=True, 
                         capture_output=True)
            
            subprocess.run(['node', node_script], 
                         cwd=temp_dir, 
                         check=True, 
                         capture_output=True)
            
            # Read the generated SVG
            with open(os.path.join(temp_dir, 'output.svg'), 'r') as f:
                svg_content = f.read()
                
            # Return the SVG object
            return SVG(svg_content)
            
        except subprocess.CalledProcessError as e:
            print("Error converting ABC to SVG:")
            print(e.stderr.decode())
            return None