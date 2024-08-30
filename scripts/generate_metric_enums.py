# Script that takes src/include/duckdb/common/enums/optimizer_type.hpp, extracts the optimizer types
# and adds them to the metrics types.
# Then it creates a new file src/include/duckdb/common/enums/metric_type.hpp with the new metrics types as enums.

import re
import os

os.chdir(os.path.dirname(__file__))

metrics_header_file = os.path.join("..", "src", "include", "duckdb", "common", "enums", "metric_type.hpp")
metrics_cpp_file = os.path.join("..", "src", "common", "enums", "metric_type.cpp")
optimizer_file = os.path.join("..", "src", "include", "duckdb", "common", "enums", "optimizer_type.hpp")

metrics = [
    "QUERY_NAME",
    "BLOCKED_THREAD_TIME",
    "CPU_TIME",
    "EXTRA_INFO",
    "CUMULATIVE_CARDINALITY",
    "OPERATOR_TYPE",
    "OPERATOR_CARDINALITY",
    "CUMULATIVE_ROWS_SCANNED",
    "OPERATOR_ROWS_SCANNED",
    "OPERATOR_TIMING",
    "RESULT_SET_SIZE",
]

phase_timing_metrics = [
    "ALL_OPTIMIZERS",
    "CUMULATIVE_OPTIMIZER_TIMING",
    "PLANNER",
    "PLANNER_BINDING",
    "PHYSICAL_PLANNER",
    "PHYSICAL_PLANNER_COLUMN_BINDING",
    "PHYSICAL_PLANNER_RESOLVE_TYPES",
    "PHYSICAL_PLANNER_CREATE_PLAN",
]

optimizer_types = []

# Regular expression to match the enum values
enum_pattern = r'\s*([A-Z_]+)\s*=\s*\d+,?|\s*([A-Z_]+),?'

inside_enum = False

# open the optimizer file and extract the optimizer types
with open(optimizer_file, "r") as f:
    for line in f:
        line = line.strip()

        if line.startswith("enum class OptimizerType"):
            inside_enum = True
            continue

        if inside_enum and line.startswith("};"):
            break

        if inside_enum:
            match = re.match(enum_pattern, line)
            if match:
                optimizer_type = match[1] if match[1] else match[2]
                if optimizer_type == "INVALID":
                    continue
                optimizer_types.append(optimizer_type)

header = """//-------------------------------------------------------------------------
//                         DuckDB
//
//
// duckdb/common/enums/metrics_type.hpp
// 
// This file is automatically generated by scripts/generate_metric_enums.py
// Do not edit this file manually, your changes will be overwritten
//-------------------------------------------------------------------------\n
"""

typedefs = """struct MetricsTypeHashFunction {
	uint64_t operator()(const MetricsType &index) const {
		return std::hash<uint8_t>()(static_cast<uint8_t>(index));
	}
};

typedef unordered_set<MetricsType, MetricsTypeHashFunction> profiler_settings_t;
typedef unordered_map<MetricsType, Value, MetricsTypeHashFunction> profiler_metrics_t;

"""

get_optimizer_metric_fun = 'GetOptimizerMetrics()'
get_phase_timing_metric_fun = 'GetPhaseTimingMetrics()'
get_optimizer_metric_by_type_fun = 'GetOptimizerMetricByType(OptimizerType type)'
get_optimizer_type_by_metric_fun = 'GetOptimizerTypeByMetric(MetricsType type)'
is_optimizer_metric_fun = 'IsOptimizerMetric(MetricsType type)'
is_phase_timing_metric_fun = 'IsPhaseTimingMetric(MetricsType type)'

metrics_class = 'MetricsUtils'

# Write the metric type header file
with open(metrics_header_file, "w") as f:
    f.write(header)

    f.write('#pragma once\n\n')
    f.write('#include "duckdb/common/types/value.hpp"\n')
    f.write('#include "duckdb/common/unordered_set.hpp"\n')
    f.write('#include "duckdb/common/unordered_map.hpp"\n')
    f.write('#include "duckdb/common/constants.hpp"\n')
    f.write('#include "duckdb/common/enum_util.hpp"\n')
    f.write('#include "duckdb/common/enums/optimizer_type.hpp"\n\n')

    f.write("namespace duckdb {\n\n")

    f.write("enum class MetricsType : uint8_t {\n")

    for metric in metrics:
        f.write(f"    {metric},\n")

    for metric in phase_timing_metrics:
        f.write(f"    {metric},\n")

    for metric in optimizer_types:
        f.write(f"    OPTIMIZER_{metric},\n")

    f.write("};\n\n")

    f.write(typedefs)

    f.write('class MetricsUtils {\n')
    f.write('public:\n')
    f.write(f'    static profiler_settings_t {get_optimizer_metric_fun};\n')
    f.write(f'    static profiler_settings_t {get_phase_timing_metric_fun};\n\n')
    f.write(f'    static MetricsType {get_optimizer_metric_by_type_fun};\n')
    f.write(f'    static OptimizerType {get_optimizer_type_by_metric_fun};\n\n')
    f.write(f'    static bool {is_optimizer_metric_fun};\n')
    f.write(f'    static bool {is_phase_timing_metric_fun};\n')
    f.write('};\n\n')

    f.write("} // namespace duckdb\n")

# Write the metric_type.cpp file
with open(metrics_cpp_file, "w") as f:
    f.write(header)

    f.write('#include "duckdb/common/enums/metric_type.hpp"\n')
    f.write("namespace duckdb {\n\n")

    f.write(f'profiler_settings_t {metrics_class}::{get_optimizer_metric_fun} {{\n')
    f.write(f"    return {{\n")
    for metric in optimizer_types:
        f.write(f"        MetricsType::OPTIMIZER_{metric},\n")
    f.write("    };\n")
    f.write("}\n\n")

    f.write(f'profiler_settings_t {metrics_class}::{get_phase_timing_metric_fun} {{\n')
    f.write(f"    return {{\n")
    for metric in phase_timing_metrics:
        f.write(f"        MetricsType::{metric},\n")
    f.write("    };\n")
    f.write("}\n\n")

    f.write(f'MetricsType {metrics_class}::{get_optimizer_metric_by_type_fun} {{\n')
    f.write('    switch(type) {\n')
    for metric in optimizer_types:
        f.write(f"        case OptimizerType::{metric}:\n")
        f.write(f"            return MetricsType::OPTIMIZER_{metric};\n")
    f.write('       default:\n')
    f.write(
        '            throw InternalException("OptimizerType %s cannot be converted to a MetricsType", '
        'EnumUtil::ToString(type));\n'
    )
    f.write('    };\n')
    f.write('}\n\n')

    f.write(f'OptimizerType {metrics_class}::{get_optimizer_type_by_metric_fun} {{\n')
    f.write('    switch(type) {\n')
    for metric in optimizer_types:
        f.write(f"        case MetricsType::OPTIMIZER_{metric}:\n")
        f.write(f"            return OptimizerType::{metric};\n")
    f.write('    default:\n')
    f.write('            return OptimizerType::INVALID;\n')
    f.write('    };\n')
    f.write('}\n\n')

    f.write(f'bool {metrics_class}::{is_optimizer_metric_fun} {{\n')
    f.write('    switch(type) {\n')
    for metric in optimizer_types:
        f.write(f"        case MetricsType::OPTIMIZER_{metric}:\n")

    f.write('            return true;\n')
    f.write('        default:\n')
    f.write('            return false;\n')
    f.write('    };\n')
    f.write('}\n\n')

    f.write(f'bool {metrics_class}::{is_phase_timing_metric_fun} {{\n')
    f.write('    switch(type) {\n')
    for metric in phase_timing_metrics:
        f.write(f"        case MetricsType::{metric}:\n")

    f.write('            return true;\n')
    f.write('        default:\n')
    f.write('            return false;\n')
    f.write('    };\n')
    f.write('}\n\n')

    f.write("} // namespace duckdb\n")
