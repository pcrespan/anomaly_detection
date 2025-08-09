package main

import (
	"bytes"
	"encoding/json"
	"io"
	"net/http"
	"os"

	"github.com/gin-gonic/gin"
	"github.com/go-playground/validator/v10"
)

var (
	TRAINER_URL   = getEnv("TRAINER_URL", "http://trainer-service:9000")
	PREDICTOR_URL = getEnv("PREDICTOR_URL", "http://predictor-service:9000")
	validate      = validator.New()
)

func getEnv(key, fallback string) string {
	if value, ok := os.LookupEnv(key); ok {
		return value
	}
	return fallback
}

type TrainData struct {
    Timestamps []int64   `json:"timestamps" validate:"required,dive,required"`
    Values     []float64 `json:"values" validate:"required,dive,required"`
}

type DataPoint struct {
	Timestamp int64   `json:"timestamp" validate:"required"`
	Value     float64 `json:"value" validate:"required"`
}

type TimeSeries struct {
	ID        string      `json:"id" validate:"required"`
	DataPoints []DataPoint `json:"data" validate:"required,dive,required"`
}

func main() {
	router := gin.Default()

	router.POST("/fit/:series_id", fitHandler)
	router.POST("/predict/:series_id", predictHandler)
	router.GET("/healthcheck", healthcheckHandler)
	router.GET("/plot", plotHandler)

	router.Run()
}

func fitHandler(c *gin.Context) {
    seriesID := c.Param("series_id")

    var trainData TrainData
    if err := c.ShouldBindJSON(&trainData); err != nil {
        c.JSON(http.StatusBadRequest, gin.H{"detail": err.Error()})
        return
    }

    if err := validate.Struct(trainData); err != nil {
        c.JSON(http.StatusBadRequest, gin.H{"detail": err.Error()})
        return
    }

    if len(trainData.Timestamps) != len(trainData.Values) || len(trainData.Timestamps) == 0 {
        c.JSON(http.StatusBadRequest, gin.H{"detail": "Timestamps and values must be of same non-zero length"})
        return
    }

    dataPoints := make([]DataPoint, len(trainData.Timestamps))
    for i := range trainData.Timestamps {
        dataPoints[i] = DataPoint{
            Timestamp: trainData.Timestamps[i],
            Value:     trainData.Values[i],
        }
    }

    timeSeries := struct {
        Data []DataPoint `json:"data"`
    }{
        Data: dataPoints,
    }

    jsonData, err := json.Marshal(timeSeries)
    if err != nil {
        c.JSON(http.StatusInternalServerError, gin.H{"detail": "failed to marshal data"})
        return
    }

    resp, err := http.Post(TRAINER_URL+"/fit/"+seriesID, "application/json", bytes.NewBuffer(jsonData))
    if err != nil {
        c.JSON(http.StatusServiceUnavailable, gin.H{"detail": err.Error()})
        return
    }
    defer resp.Body.Close()

    body, _ := io.ReadAll(resp.Body)
    if resp.StatusCode >= 400 {
        var errResp map[string]interface{}
        if err := json.Unmarshal(body, &errResp); err != nil {
            c.JSON(resp.StatusCode, gin.H{"detail": string(body)})
            return
        }
        detail, ok := errResp["detail"]
        if !ok {
            detail = "Unknown error"
        }
        c.JSON(resp.StatusCode, gin.H{"detail": detail})
        return
    }

    var result interface{}
    json.Unmarshal(body, &result)
    c.JSON(resp.StatusCode, result)
}

func predictHandler(c *gin.Context) {
	seriesID := c.Param("series_id")

	var point DataPoint
	if err := c.ShouldBindJSON(&point); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"detail": err.Error()})
		return
	}
	if err := validate.Struct(point); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"detail": err.Error()})
		return
	}

	jsonData, _ := json.Marshal(point)

	resp, err := http.Post(PREDICTOR_URL+"/predict/"+seriesID, "application/json", bytes.NewBuffer(jsonData))
	if err != nil {
		c.JSON(http.StatusServiceUnavailable, gin.H{"detail": err.Error()})
		return
	}
	defer resp.Body.Close()

	body, _ := io.ReadAll(resp.Body)
	if resp.StatusCode >= 400 {
		var errResp map[string]interface{}
		if err := json.Unmarshal(body, &errResp); err != nil {
			c.JSON(resp.StatusCode, gin.H{"detail": string(body)})
			return
		}
		detail, ok := errResp["detail"]
		if !ok {
			detail = "Unknown error"
		}
		c.JSON(resp.StatusCode, gin.H{"detail": detail})
		return
	}

	var result interface{}
	json.Unmarshal(body, &result)
	c.JSON(resp.StatusCode, result)
}

func healthcheckHandler(c *gin.Context) {
	client := &http.Client{}

	predictorResp, err := client.Get(PREDICTOR_URL + "/healthcheck")
	if err != nil {
		c.JSON(http.StatusServiceUnavailable, gin.H{"detail": "Service unavailable: " + err.Error()})
		return
	}
	defer predictorResp.Body.Close()
	predictorBody, _ := io.ReadAll(predictorResp.Body)

	trainerResp, err := client.Get(TRAINER_URL + "/healthcheck")
	if err != nil {
		c.JSON(http.StatusServiceUnavailable, gin.H{"detail": "Service unavailable: " + err.Error()})
		return
	}
	defer trainerResp.Body.Close()
	trainerBody, _ := io.ReadAll(trainerResp.Body)

	var predictorData map[string]interface{}
	var trainerData map[string]interface{}

	json.Unmarshal(predictorBody, &predictorData)
	json.Unmarshal(trainerBody, &trainerData)

	c.JSON(http.StatusOK, gin.H{
		"series_trained": predictorData["series_trained"],
		"inference_latency_ms": getMapOrDefault(predictorData, "inference_latency_ms", map[string]interface{}{"avg": 0, "p95": 0}),
		"training_latency_ms":  getMapOrDefault(trainerData, "training_latency_ms", map[string]interface{}{"avg": 0, "p95": 0}),
		"throughput": gin.H{
			"trainer":   trainerData["throughput"],
			"predictor": predictorData["throughput"],
		},
		"model_usage": predictorData["model_usage"],
		"system_metrics": gin.H{
			"trainer":   trainerData["system"],
			"predictor": predictorData["system"],
		},
	})
}

func getMapOrDefault(data map[string]interface{}, key string, defaultValue map[string]interface{}) map[string]interface{} {
	if val, ok := data[key]; ok {
		if m, ok := val.(map[string]interface{}); ok {
			return m
		}
	}
	return defaultValue
}

func plotHandler(c *gin.Context) {
	seriesID := c.Query("series_id")
	version := c.Query("version")

	client := &http.Client{}
	req, err := http.NewRequest("GET", TRAINER_URL+"/plot", nil)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"detail": err.Error()})
		return
	}

	q := req.URL.Query()
	q.Add("series_id", seriesID)
	q.Add("version", version)
	req.URL.RawQuery = q.Encode()

	resp, err := client.Do(req)
	if err != nil {
		c.JSON(http.StatusServiceUnavailable, gin.H{"detail": "Service unavailable: " + err.Error()})
		return
	}
	defer resp.Body.Close()

	body, _ := io.ReadAll(resp.Body)

	if resp.StatusCode >= 400 {
		var errResp map[string]interface{}
		if err := json.Unmarshal(body, &errResp); err != nil {
			errResp = map[string]interface{}{"detail": string(body)}
		}
		detail, ok := errResp["detail"]
		if !ok {
			detail = "Unknown error"
		}
		c.JSON(resp.StatusCode, gin.H{"detail": detail})
		return
	}

	c.Data(resp.StatusCode, "image/png", body)
}