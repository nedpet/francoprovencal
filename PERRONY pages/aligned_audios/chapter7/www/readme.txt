Web Deployment Guide
====================

This folder has everything you need to host your ReadAlong on your own server.

Your audio (chapter7.mp3), (optional) image(s) asset(s), and alignment (chapter7.readalong) are stored in this folder.

Your index.html file demonstrates the snippet and imports needed to host the ReadAlong on your server.

Please host all assets on your server, include the font and package imports defined in the index.html in your website's imports, and include the corresponding <read-along> snippet everywhere you would like your ReadAlong to be displayed.



WordPress Deployment Guide
==========================

Setup the plugin (do this once)
-------------------------------

Install and activate our plugin 'read-along-web-app-loader' on your WordPress site.

See https://github.com/ReadAlongs/Studio-Web/tree/main/packages/web-component/wordpress-plugin for more information


Deploy the read-along
---------------------

Upload the images and chapter7.readalong and chapter7.mp3 to your Media Library of your WordPress site.

Use the text editor to paste the snippet below in your WordPress page:

        ---- WP Deployment SNIPPET ----
<!-- wp:html -->
[read_along_web_app_loader version="1.5.x"]
    <read-along href="/wp-content/uploads/2026/05/chapter7.readalong" audio="/wp-content/uploads/2026/05/chapter7.mp3" image-assets-folder="/wp-content/uploads/2026/05/" theme="light" language="eng">
        <span slot='read-along-header'>Your read-along title goes here</span>
        <span slot='read-along-subheader'>Your read-along subtitle goes here</span>
    </read-along>
[/read_along_web_app_loader]
<!-- /wp:html -->
        ----- END OF SNIPPET----
