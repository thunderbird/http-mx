# http-mx

This is the simple wsgi python script behind https://mx.thunderbird.net/dns/mx/, 
which is used by Thunderbird to perform mx lookups.

The stage site can be found at https://mx-stage.thunderbird.net/dns/mx

`mx.thunderbird.net` updates when the `prod` branch has a new commit.
`mx-stage.thunderbird.net` updates when the `master` branch has a new commit.
