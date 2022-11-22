#include "duckdb/optimizer/filter_pullup.hpp"

namespace duckdb {

unique_ptr<LogicalOperator> FilterPullup::PullupBothSide(unique_ptr<LogicalOperator> op) {
	FilterPullup left_pullup(true, can_add_column);
	FilterPullup right_pullup(true, can_add_column);
	D_ASSERT(op->children[0]->GetColumnBindings().size() == op->children[1]->GetColumnBindings().size());
	op->children[0] = left_pullup.Rewrite(move(op->children[0]));
	op->children[1] = right_pullup.Rewrite(move(op->children[1]));
	D_ASSERT(left_pullup.can_add_column == can_add_column);
	D_ASSERT(right_pullup.can_add_column == can_add_column);
	D_ASSERT(op->children[0]->GetColumnBindings().size() == op->children[1]->GetColumnBindings().size());

	// merging filter expressions
	for (idx_t i = 0; i < right_pullup.filters_expr_pullup.size(); ++i) {
		left_pullup.filters_expr_pullup.push_back(move(right_pullup.filters_expr_pullup[i]));
	}

	if (!left_pullup.filters_expr_pullup.empty()) {
		return GeneratePullupFilter(move(op), left_pullup.filters_expr_pullup);
	}
	return op;
}

} // namespace duckdb
