/*
JavaScript functions for the science commissioning report
*/

function show_hide_plots(gallery_name) {
    /*
    This function enables show and hide capabilities for the plots.
    */
    var gallery = document.getElementsByName(gallery_name);

    console.log(gallery[0].style.display)

    for (i = 0; i < gallery.length; i++) {
        style = window.getComputedStyle(gallery[i]);
        style_display = style.getPropertyValue('display');

        if (style_display === "none") {
            if (gallery_name === "mosaic_gallery") {
                gallery[i].style.display = "flex";
            }
            else {
                gallery[i].style.display = "block";
            }
        }
        else {
            gallery[i].style.display = "none";
        }
    }
}