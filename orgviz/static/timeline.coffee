loadEventData = (tl, eventSource, url, callback) ->
  Timeline.loadJSON url, (timeline_data) ->
    eventSource.clear()
    eventSource.loadJSON(timeline_data, url)
    tl.layout()
    callback() if callback


panTimeline = (tl, delta) ->
  b = tl.getBand 0
  xmin = b.getMinVisibleDate().getTime()
  xmax = b.getMaxVisibleDate().getTime()
  dx = (xmax - xmin) * delta / 100
  b.setCenterVisibleDate b.getCenterVisibleDate().getTime() + dx


zoomTimeline = (tl, zoomIn) ->
  # NOTE: assuming there is only one timeline and only one band
  b = tl.getBand 0
  x = b.dateToPixelOffset b.getCenterVisibleDate().getTime()
  y = undefined  # reading the source, it seems that y is not used
  tl.zoom zoomIn, x, y, $("div.timeline-band")[0]


setupKeybinds = (tl) ->
  $(document)
    .bind("keydown", "h", (-> panTimeline tl, -10))
    .bind("keydown", "l", (-> panTimeline tl, +10))
    .bind("keydown", "o", (-> zoomTimeline tl, false))
    .bind("keydown", "i", (-> zoomTimeline tl, true))


#### setup timeline
#
# data_source: string
#     URL to load data from
setupTimeline = (data_source) ->
  zoomSteps = new Array(
    {pixelsPerInterval: 280,  unit: Timeline.DateTime.HOUR},
    {pixelsPerInterval: 140,  unit: Timeline.DateTime.HOUR},
    {pixelsPerInterval:  70,  unit: Timeline.DateTime.HOUR},
    {pixelsPerInterval:  35,  unit: Timeline.DateTime.HOUR},
    {pixelsPerInterval: 400,  unit: Timeline.DateTime.DAY},
    {pixelsPerInterval: 200,  unit: Timeline.DateTime.DAY},
    {pixelsPerInterval: 100,  unit: Timeline.DateTime.DAY},
    {pixelsPerInterval:  50,  unit: Timeline.DateTime.DAY},
    {pixelsPerInterval: 400,  unit: Timeline.DateTime.MONTH},
    {pixelsPerInterval: 200,  unit: Timeline.DateTime.MONTH},
    {pixelsPerInterval: 100,  unit: Timeline.DateTime.MONTH},
    {pixelsPerInterval:  50,  unit: Timeline.DateTime.MONTH},
    {pixelsPerInterval: 400,  unit: Timeline.DateTime.YEAR},
    {pixelsPerInterval: 200,  unit: Timeline.DateTime.YEAR},
    {pixelsPerInterval: 100,  unit: Timeline.DateTime.YEAR}
  )
  zoomIndex = 10
  eventSource = new Timeline.DefaultEventSource()

  theme = Timeline.ClassicTheme.create()
  theme.autoWidth = true
  theme.mouseWheel = 'zoom'

  bandInfos = [
    Timeline.createBandInfo(
      width:          45,
      intervalUnit:   zoomSteps[zoomIndex].unit,
      intervalPixels: zoomSteps[zoomIndex].pixelsPerInterval,
      zoomIndex:      zoomIndex,
      zoomSteps:      zoomSteps,
      eventSource:    eventSource,
      theme:          theme,
      layout:         'original',
    )
  ]

  tl_el = document.getElementById("tl")
  tl = Timeline.create(tl_el, bandInfos, Timeline.HORIZONTAL);

  loadEventData tl, eventSource, data_source, (-> setupKeybinds tl)
  $(document).bind "keydown", "g", ->
    loadEventData tl, eventSource, data_source

  resizeTimerID = null
  $(document).resize ->
    if resizeTimerID == null
      resizeTimerID = window.setTimeout(->
        resizeTimerID = null
        tl.layout()
      , 500)


root = exports ? this
root.setupTimeline = setupTimeline
