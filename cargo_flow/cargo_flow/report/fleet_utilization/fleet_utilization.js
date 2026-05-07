frappe.query_reports["Fleet Utilization"] = {
	"filters": [],

	"formatter": function(value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);

		// Highlight vehicle status with colour
		if (column.fieldname === "status") {
			const colorMap = {
				"Available":    "green",
				"On Trip":      "blue",
				"Maintenance":  "orange",
				"Out of Service": "red"
			};
			const color = colorMap[data.status] || "gray";
			value = `<span style="color: ${color}; font-weight: bold;">${data.status}</span>`;
		}

		// Highlight if total_distance is zero — vehicle is idle
		if (column.fieldname === "total_distance" && data.total_distance === 0) {
			value = `<span style="color: gray;">${value}</span>`;
		}

		return value;
	}
};
