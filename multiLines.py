
code = """
-                final JSchException schException = new JSchException("Could not send '" + localFile
+                throw new JSchException("Could not send '" + localFile

-                        + e.toString());
-                schException.initCause(e);
-                throw schException;
+                        + e.toString(), e);

"""
code = code.split('\n')
