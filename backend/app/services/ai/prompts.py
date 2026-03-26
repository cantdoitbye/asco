from typing import Dict, Any, List
from string import Template


class PromptTemplates:
    
    SYSTEM_ROLE_ROUTE_INTELLIGENCE = """You are the Route Intelligence Agent (RIA) for the Ooumph SHAKTI supply chain management system.
Your role is to analyze delivery routes, optimize logistics, and provide intelligent recommendations for supply distribution.

You have expertise in:
- Route optimization and logistics planning
- Geographic analysis and distance calculations
- Vehicle capacity and load balancing
- Traffic pattern analysis
- Fuel efficiency optimization
- Delivery time estimation

Always provide data-driven recommendations with clear reasoning."""

    SYSTEM_ROLE_SUPPLY_SENTINEL = """You are the Supply Sentinel Agent (SSA) for the Ooumph SHAKTI supply chain management system.
Your role is to monitor inventory levels, detect potential shortages, and trigger alerts for supply chain disruptions.

You have expertise in:
- Inventory management and stock monitoring
- Anomaly detection in supply patterns
- Risk assessment and mitigation
- Supplier performance analysis
- Quality control and compliance
- Emergency response protocols

Always prioritize critical alerts and provide actionable insights."""

    SYSTEM_ROLE_DEMAND_FORECAST = """You are the Demand Forecasting Agent (DFA) for the Ooumph SHAKTI supply chain management system.
Your role is to predict future demand patterns, analyze consumption trends, and recommend optimal stock levels.

You have expertise in:
- Time series analysis and forecasting
- Seasonal pattern recognition
- Statistical modeling and prediction
- Demand variability analysis
- Capacity planning
- Trend identification and extrapolation

Always provide forecasts with confidence intervals and explain your methodology."""

    ROUTE_OPTIMIZATION_TEMPLATE = Template("""Analyze and optimize the following delivery route:

Current Route Information:
- Origin: $origin
- Destinations: $destinations
- Vehicle Type: $vehicle_type
- Total Capacity: $total_capacity kg
- Current Load: $current_load kg
- Priority Deliveries: $priority_deliveries

Constraints:
- Maximum driving hours per day: $max_driving_hours
- Delivery time windows: $time_windows
- Road conditions: $road_conditions

Please provide:
1. Optimized route sequence with estimated distances
2. Fuel consumption estimate
3. Total delivery time estimate
4. Risk factors and mitigation suggestions
5. Alternative route recommendations if applicable""")

    SUPPLY_ALERT_TEMPLATE = Template("""Analyze the following supply chain data and identify potential issues:

Inventory Status:
$inventory_status

Recent Consumption Patterns:
$consumption_patterns

Supplier Information:
$supplier_info

External Factors:
- Weather conditions: $weather_conditions
- Regional events: $regional_events
- Transportation status: $transportation_status

Please provide:
1. Current inventory risk level (Low/Medium/High/Critical)
2. Items at risk of stockout within next 7 days
3. Recommended reorder quantities
4. Supplier reliability assessment
5. Suggested preventive actions""")

    DEMAND_FORECAST_TEMPLATE = Template("""Generate a demand forecast based on the following data:

Historical Consumption Data (last $historical_days days):
$historical_data

Current Inventory Levels:
$current_inventory

Upcoming Factors:
- Scheduled distributions: $scheduled_distributions
- Seasonal considerations: $seasonal_factors
- Special events: $special_events
- Anganwadi centers count: $center_count

Please provide:
1. Demand forecast for next $forecast_days days (daily breakdown)
2. Confidence level for each prediction
3. Recommended minimum stock levels
4. Expected demand variability
5. Key factors influencing the forecast""")

    ANOMALY_DETECTION_TEMPLATE = Template("""Analyze the following data for anomalies:

Data Context: $data_context

Current Readings:
$current_readings

Historical Baseline:
$historical_baseline

Expected Range:
- Minimum: $expected_min
- Maximum: $expected_max

Please identify:
1. Any detected anomalies and their severity
2. Possible causes for each anomaly
3. Impact assessment on supply chain
4. Recommended immediate actions
5. Long-term preventive measures""")

    DELIVERY_ESTIMATION_TEMPLATE = Template("""Estimate delivery timeline for the following shipment:

Shipment Details:
- Origin: $origin
- Destination: $destination
- Package weight: $weight kg
- Package dimensions: $dimensions
- Priority level: $priority

Route Information:
- Total distance: $distance km
- Number of stops: $stops
- Road type: $road_type

Please provide:
1. Estimated delivery date and time
2. Confidence level of estimate
3. Potential delays and their likelihood
4. Optimal dispatch time
5. Tracking milestones""")

    INVENTORY_RECOMMENDATION_TEMPLATE = Template("""Provide inventory recommendations based on:

Current Stock Status:
$current_stock

Demand Patterns:
$demand_patterns

Lead Times:
$lead_times

Storage Constraints:
- Maximum capacity: $max_capacity
- Temperature requirements: $temperature_req
- Shelf life considerations: $shelf_life

Please provide:
1. Reorder points for each item
2. Economic order quantities (EOQ)
3. Safety stock recommendations
4. Items requiring immediate attention
5. Storage optimization suggestions""")

    @classmethod
    def format_route_optimization(
        cls,
        origin: str,
        destinations: List[str],
        vehicle_type: str,
        total_capacity: float,
        current_load: float,
        priority_deliveries: List[str],
        max_driving_hours: float = 8.0,
        time_windows: str = "Standard business hours",
        road_conditions: str = "Normal",
    ) -> str:
        return cls.ROUTE_OPTIMIZATION_TEMPLATE.substitute(
            origin=origin,
            destinations=", ".join(destinations),
            vehicle_type=vehicle_type,
            total_capacity=total_capacity,
            current_load=current_load,
            priority_deliveries=", ".join(priority_deliveries),
            max_driving_hours=max_driving_hours,
            time_windows=time_windows,
            road_conditions=road_conditions,
        )

    @classmethod
    def format_supply_alert(
        cls,
        inventory_status: str,
        consumption_patterns: str,
        supplier_info: str,
        weather_conditions: str = "Normal",
        regional_events: str = "None",
        transportation_status: str = "Operational",
    ) -> str:
        return cls.SUPPLY_ALERT_TEMPLATE.substitute(
            inventory_status=inventory_status,
            consumption_patterns=consumption_patterns,
            supplier_info=supplier_info,
            weather_conditions=weather_conditions,
            regional_events=regional_events,
            transportation_status=transportation_status,
        )

    @classmethod
    def format_demand_forecast(
        cls,
        historical_data: str,
        current_inventory: str,
        scheduled_distributions: str,
        seasonal_factors: str,
        special_events: str,
        center_count: int,
        historical_days: int = 90,
        forecast_days: int = 30,
    ) -> str:
        return cls.DEMAND_FORECAST_TEMPLATE.substitute(
            historical_days=historical_days,
            historical_data=historical_data,
            current_inventory=current_inventory,
            scheduled_distributions=scheduled_distributions,
            seasonal_factors=seasonal_factors,
            special_events=special_events,
            center_count=center_count,
            forecast_days=forecast_days,
        )

    @classmethod
    def format_anomaly_detection(
        cls,
        data_context: str,
        current_readings: str,
        historical_baseline: str,
        expected_min: float,
        expected_max: float,
    ) -> str:
        return cls.ANOMALY_DETECTION_TEMPLATE.substitute(
            data_context=data_context,
            current_readings=current_readings,
            historical_baseline=historical_baseline,
            expected_min=expected_min,
            expected_max=expected_max,
        )

    @classmethod
    def format_delivery_estimation(
        cls,
        origin: str,
        destination: str,
        weight: float,
        dimensions: str,
        priority: str,
        distance: float,
        stops: int,
        road_type: str = "Mixed",
    ) -> str:
        return cls.DELIVERY_ESTIMATION_TEMPLATE.substitute(
            origin=origin,
            destination=destination,
            weight=weight,
            dimensions=dimensions,
            priority=priority,
            distance=distance,
            stops=stops,
            road_type=road_type,
        )

    @classmethod
    def format_inventory_recommendation(
        cls,
        current_stock: str,
        demand_patterns: str,
        lead_times: str,
        max_capacity: str,
        temperature_req: str = "Ambient",
        shelf_life: str = "Standard",
    ) -> str:
        return cls.INVENTORY_RECOMMENDATION_TEMPLATE.substitute(
            current_stock=current_stock,
            demand_patterns=demand_patterns,
            lead_times=lead_times,
            max_capacity=max_capacity,
            temperature_req=temperature_req,
            shelf_life=shelf_life,
        )
