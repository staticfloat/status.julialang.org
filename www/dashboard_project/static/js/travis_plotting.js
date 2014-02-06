// Converts the data we've received from the server to native Javascript objects
// Currently the only thing needing done is str -> Date
function convert_data(data) {
  for( key in data )
    data[key]['time'] = new Date(data[key]['time'])
  return data
}

// Given a set dates in bins, histogram data into the nearest bin
function histogram_data(data, bins) {
  pass = new Array(bins.length)
  fail = new Array(bins.length)
  for( i = 0; i < bins.length; ++i ) {
    pass[i] = 0;
    fail[i] = 0;
  }

  for( key in data ) {
    // Get the time for this particular build
    t = data[key]['time']

    // Find closest bin time
    min_idx = 0;
    for( j=1; j<bins.length; ++j ) {
      if( Math.abs(t - bins[min_idx]) > Math.abs(t - bins[j]) )
        min_idx = j;
    }

    // Increment respective output bin
    if( data[key]['result'] == 'OK' )
      pass[min_idx]++;
    else
      fail[min_idx]++;
  }
  return [pass, fail]
}

// Sorts an array of objects with 'time' keys
function sort_by_date(data) {
  data.sort(function(a,b){
    if( a['time'] < b['time'] )
      return -1
    if( a['time'] > b['time'] )
      return 1
    return 0
  })
  return data;
}

// Given the start and end date, construct a linear representation of dates
function build_xaxis(start, end, num) {
  // Default to a certain number of items between start and end (inclusive)
  num = typeof num !== 'undefined' ? num : 8

  xaxis = new Array(num)
  step = ((end - start)/(num-1))/(24*60*60*1000)

  // My naive attempt at snapping to a grid so we don't magically "lose" a day every now and then
  if( Math.abs(Math.round(step) - step) < .25 )
    step = Math.round(step)

  // Evenly space each tick
  for( i = num; i>=0; --i ) {
    xaxis[num-i] = new Date(end.getTime())
    xaxis[num-i].setDate(end.getDate() - step*i)
  }
  return xaxis;
}

// Convert a date to "mm/dd" notation
function datestr(x) {
  return (x.getMonth()+1) + '/' + x.getDate()
}

// Draw a graph for the Travis Julia tests to illustrate passing/failing tests
function update_travis_graph( data, id ) {
  if( data.length == 0 )
    return;

  // Cleanup our data
  data = convert_data(data)
  // First, sort the data by date
  data = sort_by_date(data)

  // Decide what our bins will be; if we have "enough" datapoints within the last min_time days,
  // plot only min_time days.  If not, we will plot back far enough until we have "enough"
  var enough = 40
  var min_time = 8

  // Find how far back we need to go to get min_time worth
  var i = Math.max( 0, data.length-2)
  var now = data[data.length-1]['time']
  var enough_days = min_time*24*60*60*1000
  while( i > 0 && (now - data[i]['time']) < enough_days ) {
    i--
  }

  var start = null;
  var end = data[data.length-1]['time']

  // Construct xaxis according to what data we have
  if( i <= 0 || (data.length - i) >= enough ) {
    // If we ran out of builds, or we have enough within ten days, use either
    // the start of the data we'll plot, or enough_days, whichever is more time!
    start = new Date(Math.min( end.getTime() - enough_days, data[i]['time'].getTime() ))
  } else {
    // Otherwise, use a longer window until we have enough (if possible)
    i = Math.max(0, data.length - enough)

    start = new Date(data[i]['time'])
  }
  
  // And this is our x-axis.  We'll also create a string representation
  var xaxis = build_xaxis(start, end)
  var xaxis_str = new Array(xaxis.length)

  // Check the width of bins.  If greater than 2 days, we'll give date ranges on the axis
  if( (xaxis[1] - xaxis[0]) > 2*24*60*60*1000 ) {
    var width = (xaxis[1] - xaxis[0])/2
    for( var j=0; j<xaxis.length; ++j ) {
      var x_start = new Date(xaxis[j].getTime() - width)
      var x_end = new Date(xaxis[j].getTime() + width)
      xaxis_str[j] = '(' + datestr(x_start) + ' - ' + datestr(x_end) + ')'
    }
  } else {
    for( var j=0; j<xaxis.length; ++j )
      xaxis_str[j] = datestr(xaxis[j])
  }

  // Now, histogram the data according to xaxis
  plot_series = histogram_data( data.slice(i,data.length), xaxis )

  // Finally, plot it all out!
  $('#'+id).empty()
  plotHandles[id] = $.jqplot(id, plot_series, {
    seriesDefaults: {
      renderer: $.jqplot.BarRenderer,
      rendererOptions: {
        barPadding: 4,
      }
    },

    seriesColors: ["#33bb33", "#ee0000"],

    series:[
      {label: 'Pass'},
      {label: 'Fail'},
    ],

    legend: {
      show: true,
    },

    axes: {
      xaxis: {
        renderer: $.jqplot.CategoryAxisRenderer,
        ticks: xaxis_str,
      },
    },
  })
}