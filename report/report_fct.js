/*
JavaScript functions for the science commissioning report
*/

// starting value for the slide index for the beamweights
// since there are 40 beams, we need 40 different slideshows
var slideIndex = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1];

function change_slide(n, gallery_name, label_name) {
    /*
    This function controls the galleries of the beamweights page.

    It allows to click through the images forwards and backwards. 
    It also changes the Subband value in the caption
    */
    //console.log(gallery_name)
    var i;
    // get all the elements for this gallery
    var x = document.getElementsByName(gallery_name);
    //extract the index of the slideshow from the name of the element
    slideshow_index = Number(gallery_name.replace('slideshow', ''))
    slideIndex[slideshow_index] += n;

    //console.log(slideshow_index);
    // if the slide counter is larger then the number of images, start at the beginning
    if (slideIndex[slideshow_index] > x.length) { slideIndex[slideshow_index] = 1; }
    // if the slide counter is smaller than one, go to last image
    if (slideIndex[slideshow_index] < 1) { slideIndex[slideshow_index] = x.length; }

    // hide all elements
    for (i = 0; i < x.length; i++) {
        x[i].className = x[i].className.replace("w3-show", " w3-hide");
        //x[i].style.display = "none";
    }
    // and show only the one corresponding to the slide counter
    x[slideIndex[slideshow_index] - 1].className = x[slideIndex[slideshow_index] - 1].className.replace("w3-hide", " w3-show");

    // Change the subband value in the caption
    // get the subband value
    var src_name_array = x[slideIndex[slideshow_index] - 1].src.split("/")
    var image_name = src_name_array[src_name_array.length - 1]
    var subband_value = image_name.split("_")[3].replace('S', '')
    // change the label (there is only one)
    label = document.getElementsByName(label_name);
    var old_subband_value = label[0].innerHTML.slice(-3)
    //console.log(label[0].innerHTML)
    label[0].innerHTML = label[0].innerHTML.replace(old_subband_value, subband_value)
}

function show_hide_plots(gallery_name) {
    /*
    This function enables show and hide capabilities for the plots.
    */
    // get the elements with the given name
    var gallery = document.getElementsByName(gallery_name);

    // console.log(gallery[0].style.display)

    for (i = 0; i < gallery.length; i++) {
        // switched to w3-show and w3-hide
        if (gallery[i].className.indexOf("w3-show") == -1) {
            gallery[i].className = gallery[i].className.replace("w3-hide", " w3-show");;
        } else {
            gallery[i].className = gallery[i].className.replace(" w3-show", "w3-hide");
        }

        // the following is probably not neccessary any more
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