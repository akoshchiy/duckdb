#include "duckdb/parser/expression/positional_reference_expression.hpp"

#include "duckdb/common/exception.hpp"
#include "duckdb/common/serializer.hpp"
#include "duckdb/common/types/hash.hpp"
#include "duckdb/common/to_string.hpp"

namespace duckdb {

PositionalReferenceExpression::PositionalReferenceExpression(idx_t index)
    : ParsedExpression(ExpressionType::POSITIONAL_REFERENCE, ExpressionClass::POSITIONAL_REFERENCE), index(index) {
}

string PositionalReferenceExpression::ToString() const {
	return "#" + to_string(index);
}

bool PositionalReferenceExpression::Equals(const PositionalReferenceExpression *a, const PositionalReferenceExpression *b) {
	return a->index == b->index;
}

unique_ptr<ParsedExpression> PositionalReferenceExpression::Copy() const {
	auto copy = make_unique<PositionalReferenceExpression>(index);
	copy->CopyProperties(*this);
	return move(copy);
}

hash_t PositionalReferenceExpression::Hash() const {
	hash_t result = ParsedExpression::Hash();
	return CombineHash(duckdb::Hash(index), result);
}

void PositionalReferenceExpression::Serialize(Serializer &serializer) {
	ParsedExpression::Serialize(serializer);
	serializer.Write<idx_t>(index);
}

unique_ptr<ParsedExpression> PositionalReferenceExpression::Deserialize(ExpressionType type, Deserializer &source) {
	auto expression = make_unique<PositionalReferenceExpression>(source.Read<idx_t>());
	return move(expression);
}

}
