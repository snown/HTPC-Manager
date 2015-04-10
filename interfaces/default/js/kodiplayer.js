var player = ""

function vlcProxy(vlcCmd){
 /*
 ?command=audio_track&val=<val>   
 ?command=subtitle_track&val=<val>
 > toggle pause. If current state was 'stop', play item <id>, if no <id> specified, play current item. If no current item, play 1st item in the playlist:
  ?command=pl_pause&id=<id>

> resume playback if paused, else do nothing
  ?command=pl_forceresume

> pause playback, do nothing if already paused
  ?command=pl_forcepause

> stop playback:
  ?command=pl_stop
> seek to <val>:
  ?command=seek&val=<val>
  Allowed values are of the form:
    [+ or -][<int><H or h>:][<int><M or m or '>:][<int><nothing or S or s or ">]
    or [+ or -]<int>%
    (value between [ ] are optional, value between < > are mandatory)
  examples:
    1000 -> seek to the 1000th second
    +1H:2M -> seek 1 hour and 2 minutes forward
    -10% -> seek 10% back
*/
}

function doResize(subsOnly){
    
    var playerW = $('.content').outerWidth(true);
    var playerH = $('.content').outerHeight(true);
    
    if (!subsOnly && player.media.pluginApi != null && player.media.pluginApi.setVideoSize) {
        player.media.pluginApi.setVideoSize(playerW, playerH)
    }
    
    if ($('.mejs-captions-position').length) {
        videoH = playerH
        if ((playerW / playerH) < 1.33) {videoH = playerW * 0.75;}
        lineS = videoH / 12
        subBottom = ((playerH - videoH)/2)
        if (subBottom < 35){subBottom = 35}
        $('.mejs-captions-position').css('bottom', parseInt(subBottom) + 'px');
        $('.mejs-captions-position').css('line-height', parseInt(lineS) + 'px');
        $('.mejs-captions-position').css('font-size', parseInt(lineS * 0.75) + 'px');
    }
    
}

$(document).ready(function() {
    player = new MediaElementPlayer('#player', {
            mode: mode,
            plugins: plugins,
            pluginPath: WEBDIR + "js/libs/mediaelement/",
            flashName: "flashmediaelement-cdn.swf",
            defaultVideoWidth: '100%',
            defaultVideoHeight: '100%',
            videoWidth: '100%',
            videoHeight: '100%',
            enableAutosize: true,
            setDimensions: false,
            audioWidth: 400,
            audioHeight: 30,
            startVolume: 1,
            loop: false,
            alwaysShowControls: false,
            iPadUseNativeControls: false,
            iPhoneUseNativeControls: false, 
            AndroidUseNativeControls: false,
            alwaysShowHours: false,
            enableKeyboard: false,
            pauseOtherPlayers: true,
            features: features,
            qualities: qualities,
            defaultquality: quality,
            usePluginFullScreen: false,
            keyActions: [],
            success: function(){vlcProxy(''); doResize(true)},
            customError: '<a href="">Download</a><BR />'
    });
    $(window).resize(function(){doResize(false)});
});
