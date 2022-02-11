Ignorefile
==========

To ignore certain files or directories during network creation, a :code:`.gitignore`-like ignorefile can be created at :code:`.cfgnet/ignore`.

Each line of this ignorefile contains a glob-style pattern.
Any files that match one or more of these patterns will be completely ignored by the CfgNet.