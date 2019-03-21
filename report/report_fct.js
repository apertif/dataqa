/*
JavaScript functions for the science commissioning report
*/

function show_hide_plots(gallery_name) {
    /*
    This function enables show and hide capabilities for the plots.
    */
    // get the elements with the given name
    var gallery = document.getElementsByName(gallery_name);

    // console.log(gallery[0].style.display)

    for (i = 0; i < gallery.length; i++) {
        // get the current style settings 
        // (otherwise two clicks are necessary the first time)
        style = window.getComputedStyle(gallery[i]);
        style_display = style.getPropertyValue('display');

        // if element is not visible
        if (style_display === "none") {
            // in case it belongs to the mosaic QA use flex setting
            if (gallery_name === "mosaic_gallery") {
                gallery[i].style.display = "flex";
            }
            // in case it belongs to the continuum QA use flex setting
            else if (gallery_name.indexOf("continuum_gallery") !== -1) {
                gallery[i].style.display = "flex";
            }
            // for other QA use block setting
            else {
                gallery[i].style.display = "block";
            }
        }
        else {
            gallery[i].style.display = "none";
        }
    }
}