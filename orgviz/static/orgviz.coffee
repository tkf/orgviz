#### Get a function to scroll up (if inc>0, otherwise down)
#
# This function works with scroll bar located in calendar,
# which is appeared in "agendaWeek" or "agendaDay" view.
getCalScrollUpDown = (cal, inc) ->
  ->
    view = cal.fullCalendar("getView")
    if view.name == "agendaWeek" or view.name == "agendaDay"
      # scrollBar = view.element.find('div[style*="overflow-y"]')
      scrollBar = view.element.children("div").children("div:eq(2)")
      scrollBar.scrollTop scrollBar.scrollTop() + inc
    else
      window.scrollBy 0, inc


#### Get a function to toggle "event classes"
#
# This function bind the function to
getEventclassToggleFunc = (cal, eventclass) ->
  #### refetchEvents
  # This function call `fullCalendar("refetchEvents")` will evoke
  # `getEventclasses` function, which is stored in eventSources.data
  # and will read information of eventclass from HTML form.
  refetchEvents = -> cal.fullCalendar "refetchEvents"
  checkbox = $("#eventclass-" + eventclass)
  checkbox.change refetchEvents
  getCheckedToggleFunc checkbox, refetchEvents


#### Get a function to toggle "event filters"
#
getEventfilterToggleFunc = (cal, i) ->
  #### refetchEvents
  # This function is as same as that of getEventclassToggleFunc.
  refetchEvents = -> cal.fullCalendar "refetchEvents"
  checkbox = $("#eventfilter-#{i}")
  checkbox.change refetchEvents
  getCheckedToggleFunc checkbox, refetchEvents


#### A general function to toggle checkbox and call callback if specified
#
getCheckedToggleFunc = (checkbox, callback) ->
  ->  # see: http://stackoverflow.com/questions/426258/
    if checkbox.is(":checked")
      checkbox.removeAttr "checked"
    else
      checkbox.attr "checked", "checked"
    callback()  unless callback == undefined


#### Get a function to change perspective, given its id (cpid).
#
# calendar: jquery-elem
#     $("#calendar")
# perspectives: [{"event": [string], "view": string, "filter": [string]}]
#     js object version of ORG_CAL_PERSPECTIVES
# eventclasses: {string: jquery-elem}
#     event class-to-element map
# eventfilters: {string: jquery-elem}
#     filter id-to-element map
getChoosePerspective = (calendar, perspectives, eventclasses, eventfilters) ->
  (cpid) ->
    defper = perspectives[0]  # default perspective
    per = perspectives[cpid]

    event  = if "event"  of per then per["event"]  else defper["event"]
    view   = if "view"   of per then per["view"]   else defper["view"]
    filter = if "filter" of per then per["filter"] else defper["filter"]

    for ec of eventclasses
      checkbox = eventclasses[ec]
      # event is [string]; "ec in event" (in js) can't be used.
      if ec in event  # "event.indexOf(ec) >= 0" in js
        checkbox.attr "checked", "checked"
      else
        checkbox.removeAttr "checked"
    for ef of eventfilters
      checkbox = eventfilters[ef]
      # filter is [int]
      if ef of filter  # "ef in filter" in js
        checkbox.attr "checked", "checked"
      else
        checkbox.removeAttr "checked"

    calendar
      .fullCalendar("changeView", view)
      .fullCalendar("refetchEvents")


#### Get a function to call `choosePerspective(cpid)` and check `checkbox`.
#
# cpid: string (or int)
#     perspective id
# checkbox: jquery-elem
#     this must hold: checkbox == $("#cal-perspective-#{cpid}")
# choosePerspective:
#     a function returned by getChoosePerspective
getChoosePerspectiveByKey = (cpid, checkbox, choosePerspective) -> ->
  checkbox.attr "checked", "checked"
  choosePerspective cpid


setFullCalendarUI = (events_data, perspectives) ->
  calendar = $("#calendar")
  getEventclasses = -> (k for k, v of eventclasses when v.attr("checked"))
  getEventfilters = -> (k for k, v of eventfilters when v.attr("checked"))
  eventclasses =
    deadline: $("#eventclass-deadline")
    scheduled: $("#eventclass-scheduled")
    stp: $("#eventclass-stp")
    closed: $("#eventclass-closed")
    clock: $("#eventclass-clock")
    misc: $("#eventclass-misc")

  eventfilters = {}
  $(".eventfilter").each (idx, elem) ->
    checkbox = $(elem)
    fid = checkbox.attr("id").split("eventfilter-")[1]
    eventfilters[fid] = checkbox
    checkbox.change -> calendar.fullCalendar "refetchEvents"

  calendar.fullCalendar
    header:
      left: "prev,next,today"
      center: "title"
      right: "month,basicWeek,basicDay,agendaWeek,agendaDay"

    buttonText:
      month:       "Month (q)"
      basicWeek:   "Week (w)"
      basicDay:    "Day (e)"
      agendaWeek:  "A/W (r)"
      agendaDay:   "A/D (t)"
      today:       "Today (T)"

    firstDay: 1
    eventSources: [
      {
        url: events_data
        data:
          eventclass: getEventclasses
          eventfilter: getEventfilters
      },
      {
        url: "https://www.google.com/calendar/feeds/japanese%40holiday.calendar.google.com/public/basic"
        color: "#AB8B00"
        textColor: "#AB8B00"
        backgroundColor: "white"
      },
      {
        url: "https://www.google.com/calendar/feeds/en.french%23holiday%40group.v.calendar.google.com/public/basic"
        color: "#865A5A"
        textColor: "#865A5A"
        backgroundColor: "white"
      },
      ]
    eventClick: (event) ->
      if event.url
        window.open event.url
        false

  # setup perspective and filter UI (click + key-bind)
  choosePerspective = getChoosePerspective calendar, perspectives,
    eventclasses, eventfilters
  perspectiveCheckboxes = $(".cal-perspective")

  perspectiveCheckboxes.change ->
    choosePerspective $(this).attr("id").split("cal-perspective-")[1]

  perspectiveCheckboxes.each (idx, elem) ->
    $(document).bind "keydown", "#{idx+1}",
      getChoosePerspectiveByKey idx, $(elem), choosePerspective

  $(".eventfilter").each (idx) ->
    $(document).bind "keydown", "shift+#{idx+1}",
      getEventfilterToggleFunc(calendar, idx)

  $(document).ready ->
    choosePerspective(0)  # default


setCalendarKeyBind = (doc, cal, cbConf, resizeCalendar, checkAutoReload) ->
  doc
    # show key bindings
    .bind("keydown", "shift+h", ->
      $.colorbox $.extend(href: "#help", cbConf))
    # toggle advanced control panel
    .bind("keydown", "shift+p", ->
      $("#calendar-control-advanced").toggle()
      resizeCalendar())
    # navigation
    .bind("keydown", "left", -> cal.fullCalendar "prev")
    .bind("keydown", "right", -> cal.fullCalendar "next")
    .bind("keydown", "j", getCalScrollUpDown(cal, 100))
    .bind("keydown", "k", getCalScrollUpDown(cal, -100))
    # change eventclass
    .bind("keydown", "z", getEventclassToggleFunc(cal, "deadline"))
    .bind("keydown", "x", getEventclassToggleFunc(cal, "scheduled"))
    .bind("keydown", "c", getEventclassToggleFunc(cal, "stp"))
    .bind("keydown", "v", getEventclassToggleFunc(cal, "closed"))
    .bind("keydown", "b", getEventclassToggleFunc(cal, "clock"))
    .bind("keydown", "n", getEventclassToggleFunc(cal, "misc"))
    # change views
    .bind("keydown", "q", -> cal.fullCalendar "changeView", "month")
    .bind("keydown", "w", -> cal.fullCalendar "changeView", "basicWeek")
    .bind("keydown", "e", -> cal.fullCalendar "changeView", "basicDay")
    .bind("keydown", "r", -> cal.fullCalendar "changeView", "agendaWeek")
    .bind("keydown", "t", -> cal.fullCalendar "changeView", "agendaDay")
    # toggle auto-reload calendar
    .bind("keydown", "shift+a",
      getCheckedToggleFunc($("#auto-reload"), checkAutoReload))
    # go to the current day
    .bind("keydown", "shift+t", -> cal.fullCalendar "today")
    # reload calendar
    .bind("keydown", "shift+r", -> cal.fullCalendar "refetchEvents")
    # open timeline page
    .bind("keydown", "shift+l",
      -> window.open $("#timeline_link").attr("href") )


#### Get a function to check the input checkbox and start/stop auo-reload
#
getCheckAutoReload = (cal) ->
  autoReloadId = false
  autoReload = ->  # see: http://stackoverflow.com/questions/1036612/
    autoReloadId = window.setTimeout(->
      cal.fullCalendar "refetchEvents"
      autoReload()
    , 1000)

  # return checkAutoReload
  ->
    if $("#auto-reload").is(":checked")
      autoReload()
    else
      clearTimeout autoReloadId


#### Get a function to resize FullCalendar to fit with window size.
#
getResizeCalendar = (cal) -> ->
  cal.fullCalendar "option", "height",
    $(window).height() - cal.position().top


#### Setup everything except for setFullCalendarUI
#
setCalendarKeyBindAndAutoResizeAndAutoReloadAndHelp = ->
  $("#calendar-control-advanced").hide()

  cbConf =  # ColorBox configuration
    transition: "none"
    speed: 0
    inline: true

  cal = $("#calendar")
  resizeCalendar = getResizeCalendar(cal)
  checkAutoReload = getCheckAutoReload()

  setCalendarKeyBind($(document), cal, cbConf, resizeCalendar, checkAutoReload)

  $(window).bind "resize", resizeCalendar  # auto-resize
  resizeCalendar()

  $("#auto-reload").change checkAutoReload  # auto-reload
  checkAutoReload()

  $(".inline").colorbox cbConf  # this is for help


#### Setup everything for calendar page
#
setCalendar = (events_data, perspectives) ->
  setFullCalendarUI(events_data, perspectives)
  setCalendarKeyBindAndAutoResizeAndAutoReloadAndHelp()


#### Get a function to switch page to `page`
#
# page: {"calendar", "graphs", "dones"}
#     page to switch to
# faviconpath: string
#     a path to favicon of this page
# callback: callable
#     this will be called at end of the returned function
getPageSwitcher = (page, faviconpath, callback) ->
  pagelist = ["calendar", "graphs", "dones"]
  otherpages = (p for p in pagelist when p isnt page)
  title = $("title")
  ->
    $("#container-#{ page }").show()
    for other in otherpages
      $("#container-#{ other }").hide()
    changeFavicon faviconpath
    title.text("#{ page } | orgviz")
    callback() if callback?


#### Change favicon to the given URL.
#
changeFavicon = (href) ->
  # http://stackoverflow.com/questions/260857/
  # Note: I implemented using jquery but did not work
  link = document.createElement("link")
  link.id = "favicon"
  link.type = "image/x-icon"
  link.rel = "shortcut icon"
  link.href = href
  $("#favicon").remove()
  document.getElementsByTagName("head")[0].appendChild link


#### Setup key-bind for transition between calendar, graphs and dones pages
#
setPageViewKeyBind = (favicon) ->
  reloadImages = getReloadImages($(".graph"))
  viewPageCalendar = getPageSwitcher "calendar", favicon.calendar
  viewPageGraphs = getPageSwitcher "graphs", favicon.graphs, reloadImages
  viewPageDones = getPageSwitcher(
    "dones", favicon.dones,
    ->
      $.ajax
        url: "/dones_data"
        success: (data) -> $("#container-dones").html data
  )
  viewPageCalendar()
  $(document)
    .bind("keydown", "g", reloadImages)
    .bind("keydown", "shift+c", viewPageCalendar)
    .bind("keydown", "shift+g", viewPageGraphs)
    .bind("keydown", "shift+d", viewPageDones)


#### Get a function to reload given images
#
# images: jq-elem
#    such as $(".graph").
getReloadImages = (images) ->
  imgSrcMap = {}
  imgsGraph = images

  # store id -> src map, before src is contaminated by ?param=val&...
  imgsGraph.each (index, elem) ->
    id = $(elem).attr("id")
    if id
      imgSrcMap[id] = $(elem).attr("src")
    else
      id = "graph-" + index
      $(elem).attr "id", id
      imgSrcMap[id] = $(elem).attr("src")

  ->
    imgsGraph.attr "src", ->
      id = $(this).attr("id")
      # add ?_=date to force browser to reload image
      newSrc = imgSrcMap[id] + "?_=" + new Date().getTime()
      newSrc  # = $(this).attr("src", newSrc)


#### Setup pages for calendar, graphs, dones
#
# events_data and perspectives will be passed setCalendar.
setOrgGtdWeb = (events_data, perspectives, favicon) ->
  setCalendar events_data, perspectives
  setPageViewKeyBind favicon


# export functions as global function
# see: http://stackoverflow.com/questions/4214731/
root = exports ? this
root.setOrgGtdWeb = setOrgGtdWeb
root.setCalendar = setCalendar
root.getReloadImages = getReloadImages
