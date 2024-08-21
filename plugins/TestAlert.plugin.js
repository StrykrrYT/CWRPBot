/**
 * @name ScrollerChangeAlert
 * @description A BetterDiscord plugin that alerts when the 'markup_d6076c' div element changes and highlights specified hex values.
 * @version 1.0.0
 * @author Your Name
 */

module.exports = class ScrollerChangeAlert {
    constructor() {
        this.observer = null;
        this.highlightedHexValues = ['#ff0000', '#00ff00', '#0000ff']; // Example: Array of hex values to highlight
    }

    // Called when the plugin is started
    start() {
        console.log('ScrollerChangeAlert plugin started');
        
        // Define the target element to observe
        const targetSelector = '.markup_d6076c'; // Replace with your specific selector
        
        // Create a new observer instance
        this.observer = new MutationObserver(mutationsList => {
            for (let mutation of mutationsList) {
                if (mutation.type === 'childList' || mutation.type === 'attributes') {
                    const targetElement = mutation.target;
                    
                    // Check if the mutation includes the text "bob" or matches any highlighted hex value
                    let contentChanged = false;
                    if (targetElement.textContent.includes('bob')) {
                        console.log('SCROLLER CHANGED and includes "bob"');
                        contentChanged = true;
                    }
                    
                    this.highlightedHexValues.forEach(hex => {
                        const regex = new RegExp(`#${hex.slice(1)}`, 'gi'); // Create regex to match hex value
                        if (regex.test(targetElement.textContent)) {
                            console.log(`SCROLLER CHANGED and includes "${hex}"`);
                            contentChanged = true;
                        }
                    });
                    
                    if (contentChanged) {
                        // Example: Highlight the text
                        targetElement.innerHTML = targetElement.innerHTML.replace(/(#[0-9a-fA-F]{6})/g, '<span style="background-color: yellow;">$1</span>');
                        
                        // Alert the user with a popup
                        alert('SCROLLER CHANGED and includes "bob" or highlighted hex value');
                    } else {
                        console.log('SCROLLER CHANGED but does not include "bob" or highlighted hex value');
                    }
                }
            }
        });
        
        // Start observing the target element for mutations
        const targetElement = document.querySelector(targetSelector);
        if (targetElement) {
            this.observer.observe(targetElement, { attributes: true, childList: true, subtree: true });
        } else {
            console.error(`Element with selector '${targetSelector}' not found`);
        }
    }

    // Called when the plugin is stopped
    stop() {
        console.log('ScrollerChangeAlert plugin stopped');
    
        // Disconnect the observer when stopping the plugin
        if (this.observer) {
            this.observer.disconnect();
            this.observer = null;
        }
    }

    // Called when the plugin is loaded for the first time
    load() {
        console.log('ScrollerChangeAlert plugin loaded');
        this.start();
    }
};
