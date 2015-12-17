#freewheel#

This is an experiment in embedding functionality into images with the goal of sharing pieces of interactive content through existing channels (like Twitter and Facebook). Rebekah Cox [originally proposed the idea][1].

Using the bootstrap page, the user can embed JavaScript and a state dictionary into an image. The JavaScript is given a canvas to draw on, the state dictionary, and a callback to call with the new state when a new image should be generated.

That initial image and images like it can be loaded by the host page. The user can then interact with the content and when the content calls its completion handler, a new image is generated with new state embedded.

No server component is necessary.

##Results##
freewheel works... kind of. Code and state can be embedded in an image and it can be loaded by another user who has the resulting PNG.

In practice, I haven't yet achieved freewheel's goals because the expected means of sharing the PNG do not work in practice. Both Facebook and Twitter reencode content as JPEG which totally trashes the naive pixel encoding.

I'm sure there is plenty of research into encoding data into images (steganography). I'd like the encoding to be able to survive a few interesting events:

 * Screenshotting on mobile devices (with varying DPIs)
 * Transmission over social networks
 * Cropping/uncropping
 * All kinds of [shitpic][2] stuff

I'll probably look into those techniques and see how far this could go. [Andrew Wansley][3] suggests [High Capacity Color Barcode][4] might be something to look into, and also Snapchat seems to have done a lot with QR codes that could help.

In the meantime, if you have a means of sharing images losslessly you can play my shitty version of Checkers with a friend! Save this image and upload it to https://jasonprado.github.io/freewheel/host.html to take a turn.

![Checkers](https://raw.github.com/jasonprado/freewheel/master/reds_turn.png)

[1]:https://twitter.com/artypapers/status/677212283634782208
[2]:http://www.theawl.com/2014/12/the-triumphant-rise-of-the-shitpic
[3]:https://github.com/awans
[4]:https://en.wikipedia.org/wiki/High_Capacity_Color_Barcode