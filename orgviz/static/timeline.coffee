#### Fit `fit` element to `to` element
fitTo = (fit, to, bottom = 0, right = 0) ->
  pos = fit.position()
  fit.height(to.height() - pos.top - bottom)
  fit.width(to.width() - pos.left - right)


#### Get a function resize timeglider to window
getResizeTimeGlider = (tg) ->
  tgcont = tg.children(".timeglider-container")
  win = $(window)
  ->
    fitTo tg, win
    fitTo tgcont, win


#### Get a function to check the input checkbox and start/stop auo-reload
#
getCheckAutoReload = (reload) ->
  autoReloadId = false
  autoReload = ->  # see: http://stackoverflow.com/questions/1036612/
    autoReloadId = window.setTimeout(->
      reload()
      autoReload()
    , 1000)

  # return checkAutoReload
  ->
    if $("#auto-reload").is(":checked")
      autoReload()
    else
      clearTimeout autoReloadId


#### A general function to toggle checkbox and call callback if specified
#
getCheckedToggleFunc = (checkbox, callback) ->
  ->  # see: http://stackoverflow.com/questions/426258/
    if checkbox.is(":checked")
      checkbox.removeAttr "checked"
    else
      checkbox.attr "checked", "checked"
    callback() if callback?


#### Get a function to emulate mouse push of `delay` time
#
getPushPan = (left, right, delay) ->
  tid = false
  pushed = false
  push = (button) ->
    if not pushed
      pushed = true
      button.mousedown()
      tid = window.setTimeout( ->
        pushed = false
        button.mouseup()
      , delay)
  [(-> push left), (-> push right)]


#### setup timeline
#
# tg: jq-element
#     e.g.: $("#placement")
# data_source: string
#     URL to load data from
setupTimeline = (tg, data_source) ->
  # make tg 100% height/width, before setting up timeglider
  fitTo tg, $(window), 10  # 10px offset at bottom

  tg.timeline(
    min_zoom: 1
    max_zoom: 40
    data_source: data_source
  )

  tg_actor = tg.data("timeline")

  # set auto-reload
  autoReloadCheckbox = $("#auto-reload")
  checkAutoReload = getCheckAutoReload(-> tg_actor.load data_source)
  autoReloadCheckbox.change checkAutoReload
  checkAutoReload()

  # there is no "pan" api, so just push these buttons!
  panButtonLeft  = $(".timeglider-pan-left")
  panButtonRight = $(".timeglider-pan-right")
  [pushLeft, pushRight] = getPushPan panButtonLeft, panButtonRight, 100

  $(document)
    .bind("keydown", "r", -> tg_actor.load data_source)
    .bind("keydown", "a",
      getCheckedToggleFunc autoReloadCheckbox, checkAutoReload)
    .bind("keydown", "i", -> tg_actor.zoom -1)  # zoom-in
    .bind("keydown", "o", -> tg_actor.zoom +1)  # zoom-out
    .bind("keydown", "h", pushLeft)
    .bind("keydown", "l", pushRight)
    #### binding keyup/down to moudeup/down didn't work
    # .bind("keydown", "h", -> panButtonLeft.mousedown())
    # .bind("keydown", "l", -> panButtonRight.mousedown())
    # .bind("keyup", "h", -> panButtonLeft.mouseup())
    # .bind("keyup", "l", -> panButtonRight.mouseup())
    #### this seems to have no effect...
    .bind("keydown", "g", ->
      panButtonLeft.mouseup()
      panButtonRight.mouseup()
      console.log("G!"))

  # this did not work.  height can't be re-fitted.
  # # auto-resize
  # resizeTimeGlider = getResizeTimeGlider(tg)
  # $(window).bind "resize", resizeTimeGlider
  # resizeTimeGlider()

  # return
  tg: tg
  tg_actor: tg_actor


root = exports ? this
root.setupTimeline = setupTimeline
