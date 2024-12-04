export default function initChart(ticker, histData) {
  am5.ready(function () {
    var root = am5.Root.new("chartdiv");
    const myTheme = am5.Theme.new(root);
    myTheme.rule("Grid", ["scrollbar", "minor"]).setAll({
      visible: false,
    });
    root.setThemes([am5themes_Animated.new(root), myTheme]);

    var stockChart = root.container.children.push(
      am5stock.StockChart.new(root, {
        paddingRight: 0,
      })
    );

    root.numberFormatter.set("numberFormat", "#,###.00");

    var mainPanel = stockChart.panels.push(
      am5stock.StockPanel.new(root, {
        wheelY: "zoomX",
        panX: true,
        panY: true,
      })
    );

    var valueAxis = mainPanel.yAxes.push(
      am5xy.ValueAxis.new(root, {
        renderer: am5xy.AxisRendererY.new(root, { pan: "zoom" }),
        extraMin: 0.1,
        tooltip: am5.Tooltip.new(root, {}),
        numberFormat: "#,###.00",
        extraTooltipPrecision: 2,
      })
    );

    var dateAxis = mainPanel.xAxes.push(
      am5xy.GaplessDateAxis.new(root, {
        groupData: true,
        baseInterval: { timeUnit: "minute", count: 1 },
        renderer: am5xy.AxisRendererX.new(root, {
          minGridDistance: 50,
          cellStartLocation: 0.1,
          cellEndLocation: 0.9,
          minorGridEnabled: true,
        }),
        tooltip: am5.Tooltip.new(root, {}),
        dateFormats: {
          millisecond: "mm:ss",
          second: "HH:mm:ss",
          minute: "HH:mm",
          hour: "HH:mm",
          day: "MMM dd",
          week: "MMM dd",
          month: "MMM yyyy",
          year: "yyyy",
        },
        periodChangeDateFormats: {
          millisecond: "HH:mm:ss",
          second: "HH:mm:ss",
          minute: "HH:mm",
          hour: "HH:mm",
          day: "MMM dd",
          week: "MMM dd",
          month: "MMM yyyy",
          year: "yyyy",
        },
      })
    );

    var valueSeries = mainPanel.series.push(
      am5xy.CandlestickSeries.new(root, {
        name: "Stock Data",
        clustered: false,
        valueXField: "Date",
        valueYField: "Close",
        highValueYField: "High",
        lowValueYField: "Low",
        openValueYField: "Open",
        calculateAggregates: true,
        xAxis: dateAxis,
        yAxis: valueAxis,
        legendValueText:
          "open: [bold]{openValueY}[/] high: [bold]{highValueY}[/] low: [bold]{lowValueY}[/] close: [bold]{valueY}[/]",
      })
    );

    stockChart.set("stockSeries", valueSeries);

    var valueLegend = mainPanel.plotContainer.children.push(
      am5stock.StockLegend.new(root, {
        stockChart: stockChart,
      })
    );

    // Volume axis configuration
    var volumeAxisRenderer = am5xy.AxisRendererY.new(root, {
      inside: true,
    });
    volumeAxisRenderer.labels.template.set("forceHidden", true);
    volumeAxisRenderer.grid.template.set("forceHidden", true);

    var volumeValueAxis = mainPanel.yAxes.push(
      am5xy.ValueAxis.new(root, {
        numberFormat: "#.#a",
        height: am5.percent(20),
        y: am5.percent(100),
        centerY: am5.percent(100),
        renderer: volumeAxisRenderer,
      })
    );

    var volumeSeries = mainPanel.series.push(
      am5xy.ColumnSeries.new(root, {
        name: "Volume",
        clustered: false,
        valueXField: "Date",
        valueYField: "Volume",
        xAxis: dateAxis,
        yAxis: volumeValueAxis,
        legendValueText: "[bold]{valueY.formatNumber('#,###.0a')}[/]",
      })
    );

    volumeSeries.columns.template.setAll({
      strokeOpacity: 0,
      fillOpacity: 0.5,
    });

    stockChart.set("volumeSeries", volumeSeries);
    valueLegend.data.setAll([valueSeries, volumeSeries]);

    // Cursor configuration
    mainPanel.set(
      "cursor",
      am5xy.XYCursor.new(root, {
        yAxis: valueAxis,
        xAxis: dateAxis,
        snapToSeries: [valueSeries],
        snapToSeriesBy: "y!",
      })
    );

    // Scrollbar configuration
    var scrollbar = mainPanel.set(
      "scrollbarX",
      am5xy.XYChartScrollbar.new(root, {
        orientation: "horizontal",
        height: 50,
      })
    );
    stockChart.toolsContainer.children.push(scrollbar);

    var sbDateAxis = scrollbar.chart.xAxes.push(
      am5xy.GaplessDateAxis.new(root, {
        baseInterval: { timeUnit: "minute", count: 1 },
        renderer: am5xy.AxisRendererX.new(root, {
          minGridDistance: 50,
          cellStartLocation: 0.1,
          cellEndLocation: 0.9,
        }),
      })
    );

    var sbValueAxis = scrollbar.chart.yAxes.push(
      am5xy.ValueAxis.new(root, {
        renderer: am5xy.AxisRendererY.new(root, {}),
      })
    );

    var sbSeries = scrollbar.chart.series.push(
      am5xy.LineSeries.new(root, {
        valueYField: "Close",
        valueXField: "Date",
        xAxis: sbDateAxis,
        yAxis: sbValueAxis,
      })
    );

    sbSeries.fills.template.setAll({
      visible: true,
      fillOpacity: 0.3,
    });

    // Set up interval control
    var defaultInterval = "1d";
    var intervalControl = am5stock.IntervalControl.new(root, {
      stockChart: stockChart,
      currentItem: defaultInterval,
      intervals: [
        { id: "1m", label: "1m", interval: { timeUnit: "minute", count: 1 } },
        { id: "2m", label: "2m", interval: { timeUnit: "minute", count: 2 } },
        { id: "5m", label: "5m", interval: { timeUnit: "minute", count: 5 } },
        {
          id: "15m",
          label: "15m",
          interval: { timeUnit: "minute", count: 15 },
        },
        {
          id: "30m",
          label: "30m",
          interval: { timeUnit: "minute", count: 30 },
        },
        { id: "60m", label: "1h", interval: { timeUnit: "hour", count: 1 } },
        { id: "1d", label: "1d", interval: { timeUnit: "day", count: 1 } },
        { id: "5d", label: "5d", interval: { timeUnit: "day", count: 5 } },
        { id: "1wk", label: "1w", interval: { timeUnit: "week", count: 1 } },
        { id: "1mo", label: "1M", interval: { timeUnit: "month", count: 1 } },
      ],
    });

    // Data fetching and updating functions
    function fetchData(interval) {
      interval = interval.replace(/\s+/g, "");
      return fetch(`/update_data/${encodeURIComponent(ticker)}/${interval}/`)
        .then((response) => {
          if (!response.ok) {
            throw new Error("Network response was not ok");
          }
          return response.json();
        })
        .then((data) => {
          if (data && data.length > 0) {
            return data.map(function (item) {
              return {
                Date: new Date(item.Datetime).getTime(),
                Open: item.Open,
                High: item.High,
                Low: item.Low,
                Close: item.Close,
                Volume: item.Volume,
              };
            });
          }
          throw new Error("No data available for this interval");
        });
    }

    function updateChart(updatedData, interval) {
      if (updatedData.length === 0) {
        console.error("No data available to update chart");
        return;
      }

      valueSeries.data.setAll(updatedData);
      volumeSeries.data.setAll(updatedData);
      sbSeries.data.setAll(updatedData);

      var axisConfig = getAxisConfig(interval);
      dateAxis.set("baseInterval", axisConfig.baseInterval);
      dateAxis.set("groupInterval", axisConfig.groupInterval);
      dateAxis.set("groupCount", axisConfig.groupCount);
      dateAxis.set("dateFormats", axisConfig.dateFormats);
      dateAxis.set(
        "periodChangeDateFormats",
        axisConfig.periodChangeDateFormats
      );

      var lastIndex = updatedData.length - 1;
      var startIndex = Math.max(0, lastIndex - axisConfig.visiblePoints);
      var startDate = updatedData[startIndex].Date;
      var endDate = updatedData[lastIndex].Date;
      dateAxis.zoomToDates(new Date(startDate), new Date(endDate));
    }

    function getAxisConfig(interval) {
      const config = {
        baseInterval: { timeUnit: "minute", count: 1 },
        groupInterval: { timeUnit: "minute", count: 1 },
        groupCount: 200,
        visiblePoints: 30,
        dateFormats: {
          minute: "HH:mm",
          hour: "HH:mm",
          day: "MMM dd",
          week: "MMM dd",
          month: "MMM yyyy",
        },
        periodChangeDateFormats: {
          minute: "HH:mm",
          hour: "HH:mm",
          day: "MMM dd",
          week: "MMM dd",
          month: "MMM yyyy",
        },
      };

      switch (interval) {
        case "1m":
          config.baseInterval = { timeUnit: "minute", count: 1 };
          config.groupInterval = { timeUnit: "minute", count: 1 };
          config.visiblePoints = 60;
          break;
        case "2m":
          config.baseInterval = { timeUnit: "minute", count: 2 };
          config.groupInterval = { timeUnit: "minute", count: 2 };
          config.visiblePoints = 50;
          break;
        case "5m":
          config.baseInterval = { timeUnit: "minute", count: 5 };
          config.groupInterval = { timeUnit: "minute", count: 5 };
          config.visiblePoints = 40;
          break;
        case "15m":
          config.baseInterval = { timeUnit: "minute", count: 15 };
          config.groupInterval = { timeUnit: "minute", count: 15 };
          config.visiblePoints = 35;
          break;
        case "30m":
          config.baseInterval = { timeUnit: "minute", count: 30 };
          config.groupInterval = { timeUnit: "minute", count: 30 };
          config.visiblePoints = 30;
          break;
        case "60m":
          config.baseInterval = { timeUnit: "hour", count: 1 };
          config.groupInterval = { timeUnit: "hour", count: 1 };
          config.visiblePoints = 24;
          break;
        case "1d":
          config.baseInterval = { timeUnit: "day", count: 1 };
          config.groupInterval = { timeUnit: "day", count: 1 };
          config.visiblePoints = 30;
          break;
        case "5d":
          config.baseInterval = { timeUnit: "day", count: 5 };
          config.groupInterval = { timeUnit: "day", count: 5 };
          config.visiblePoints = 20;
          break;
        case "1wk":
          config.baseInterval = { timeUnit: "week", count: 1 };
          config.groupInterval = { timeUnit: "week", count: 1 };
          config.visiblePoints = 12;
          config.dateFormats.week = "MMM dd";
          config.periodChangeDateFormats.week = "MMM dd, yyyy";
          break;
        case "1mo":
          config.baseInterval = { timeUnit: "month", count: 1 };
          config.groupInterval = { timeUnit: "month", count: 1 };
          config.visiblePoints = 12;
          config.dateFormats.month = "MMM yyyy";
          config.periodChangeDateFormats.month = "MMM yyyy";
          break;
      }

      return config;
    }

    // Initial data fetch and chart update
    fetchData(defaultInterval)
      .then((updatedData) => {
        updateChart(updatedData, defaultInterval);
      })
      .catch((error) => {
        console.error("Error fetching initial data:", error);
        // Display an error message to the user
        document.getElementById(
          "chartdiv"
        ).innerHTML = `<p>Error loading chart data: ${error.message}</p>`;
      });

    // Set up interval change handler
    intervalControl.events.on("selected", function (ev) {
      var interval = ev.item.id;
      fetchData(interval)
        .then((updatedData) => {
          updateChart(updatedData, interval);
        })
        .catch((error) => {
          console.error("Error fetching data:", error);
        });
    });

    // Series type switcher
    var seriesSwitcher = am5stock.SeriesTypeControl.new(root, {
      stockChart: stockChart,
    });

    seriesSwitcher.events.on("selected", function (ev) {
      setSeriesType(ev.item.id);
    });

    function getNewSettings(series) {
      var newSettings = [];
      am5.array.each(
        [
          "name",
          "valueYField",
          "highValueYField",
          "lowValueYField",
          "openValueYField",
          "calculateAggregates",
          "valueXField",
          "xAxis",
          "yAxis",
          "legendValueText",
          "stroke",
          "fill",
        ],
        function (setting) {
          newSettings[setting] = series.get(setting);
        }
      );
      return newSettings;
    }

    function setSeriesType(seriesType) {
      var currentSeries = stockChart.get("stockSeries");
      var newSettings = getNewSettings(currentSeries);
      var data = currentSeries.data.values;
      mainPanel.series.removeValue(currentSeries);
      var series;

      switch (seriesType) {
        case "line":
          series = mainPanel.series.push(
            am5xy.LineSeries.new(root, newSettings)
          );
          break;
        case "candlestick":
        case "procandlestick":
          newSettings.clustered = false;
          series = mainPanel.series.push(
            am5xy.CandlestickSeries.new(root, newSettings)
          );
          if (seriesType == "procandlestick") {
            series.columns.template.get("themeTags").push("pro");
          }
          break;
        case "ohlc":
          newSettings.clustered = false;
          series = mainPanel.series.push(
            am5xy.OHLCSeries.new(root, newSettings)
          );
          break;
      }

      if (series) {
        valueLegend.data.removeValue(currentSeries);
        series.data.setAll(data);
        stockChart.set("stockSeries", series);
        var cursor = mainPanel.get("cursor");
        if (cursor) {
          cursor.set("snapToSeries", [series]);
        }
        valueLegend.data.insertIndex(0, series);
      }
    }

    // Set up toolbar
    var toolbar = am5stock.StockToolbar.new(root, {
      container: document.getElementById("chartcontrols"),
      stockChart: stockChart,
      controls: [
        intervalControl,
        am5stock.IndicatorControl.new(root, {
          stockChart: stockChart,
          legend: valueLegend,
        }),
        am5stock.DrawingControl.new(root, {
          stockChart: stockChart,
        }),
        seriesSwitcher,
        am5stock.ResetControl.new(root, {
          stockChart: stockChart,
        }),
        am5stock.SettingsControl.new(root, {
          stockChart: stockChart,
        }),
      ],
    });

    // Load initial data
    var transformedData = histData.map(function (item) {
      return {
        Date: new Date(item.Datetime).getTime(),
        Open: item.Open,
        High: item.High,
        Low: item.Low,
        Close: item.Close,
        Volume: item.Volume,
      };
    });

    valueSeries.data.setAll(transformedData);
    volumeSeries.data.setAll(transformedData);
    sbSeries.data.setAll(transformedData);
  });
}
