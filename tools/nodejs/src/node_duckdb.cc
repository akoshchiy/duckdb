#include <stdint.h>
#include <sstream>
#include <cstring>
#include <string>

#include "macros.h"
#include "database.h"
#include "statement.h"

using namespace node_duckdb;

namespace {

Napi::Object RegisterModule(Napi::Env env, Napi::Object exports) {
    Napi::HandleScope scope(env);

    Database::Init(env, exports);
    Statement::Init(env, exports);

    exports.DefineProperties({
	    DEFINE_CONSTANT_INTEGER(exports, DUCKDB_NODEJS_ERROR, ERROR)

        DEFINE_CONSTANT_INTEGER(exports, DUCKDB_NODEJS_READONLY, OPEN_READONLY) // same as SQLite
        DEFINE_CONSTANT_INTEGER(exports, 0, OPEN_READWRITE) // ignored
        DEFINE_CONSTANT_INTEGER(exports, 0, OPEN_CREATE) // ignored
        DEFINE_CONSTANT_INTEGER(exports, 0, OPEN_FULLMUTEX) // ignored
        DEFINE_CONSTANT_INTEGER(exports, 0, OPEN_SHAREDCACHE) // ignored
        DEFINE_CONSTANT_INTEGER(exports, 0, OPEN_PRIVATECACHE) // ignored

    });

    return exports;
}

}

NODE_API_MODULE(node_duckdb, RegisterModule)
