#### setup timeline
#
# data_source: string
#     URL to load data from
setupTimeline = (data_source) ->
  Timeline.loadJSON data_source, (timeline_data) ->
    tl_el = document.getElementById("tl")
    eventSource1 = new Timeline.DefaultEventSource()

    theme1 = Timeline.ClassicTheme.create()
    theme1.autoWidth = true
    theme1.mouseWheel = 'zoom'

    bandInfos = [
      Timeline.createBandInfo(
        width:          45,
        intervalUnit:   Timeline.DateTime.MONTH,
        intervalPixels: 100,
        eventSource:    eventSource1,

        zoomIndex:      10,
        zoomSteps:      new Array(
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
        ),

        theme:          theme1,
        layout:         'original',
      )
    ]

    tl = Timeline.create(tl_el, bandInfos, Timeline.HORIZONTAL);

    url = '.'
    eventSource1.loadJSON(timeline_data, url)
    tl.layout()


resizeTimerID = null
onResize = ->
  if resizeTimerID == null
    resizeTimerID = window.setTimeout(->
      resizeTimerID = null
      tl.layout()
    , 500)


root = exports ? this
root.setupTimeline = setupTimeline
root.onResize = onResize
