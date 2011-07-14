import re
import uuid

def with_soap_attachment(suds_method, attachment_data, *args, **kwargs):
    """ Add an attachment to a suds soap request.

    attachment_data is assumed to contain a list:
      ( <attachment content>, <content id>, <mime-type> )

    The attachment content is only required required list element.
    """
    from suds.transport import Request

    # Suds doesn't currently support SOAP Attachments, so we have to build our
    # own attachment support, using parts of the suds library

    MIME_DEFAULT = 'text/plain'
    attachment_transfer_encoding = '8bit'
    soap_method = suds_method.method

    if len(attachment_data) == 3:
        data, attachment_id, attachment_mimetype = attachment_data
    elif len(attachment_data) == 2:
        data, attachment_id = attachment_data
        attachment_mimetype = MIME_DEFAULT
    elif len(attachment_data) == 1:
        data = attachment_data
        attachment_mimetype = MIME_DEFAULT
        attachment_id = uuid.uuid4()

    # Generate SOAP XML appropriate for this request
    soap_client = suds_method.clientclass(kwargs)
    binding = soap_method.binding.input
    soap_xml = binding.get_message(soap_method, args, kwargs)

    # Prepare MIME headers & boundaries
    boundary_id = 'uuid:%s' % uuid.uuid4()
    root_part_id ='uuid:%s' % uuid.uuid4()
    request_headers = {
      'Content-Type': '; '.join([
          'multipart/related',
          'type="text/xml"',
          'start="<%s>"' % root_part_id,
          'boundary="%s"' % boundary_id,
        ]),
    }
    soap_headers = '\n'.join([
      'Content-Type: text/xml; charset=UTF-8',
      'Content-Transfer-Encoding: 8bit',
      'Content-Id: <%s>' % root_part_id,
      '',
    ])
    attachment_headers = '\n'.join([
      'Content-Type: %s' % attachment_mimetype,
      'Content-Transfer-Encoding: %s' % attachment_transfer_encoding,
      'Content-Id: <%s>' % attachment_id,
      '',
    ])

    # Build the full request
    request_text = '\n'.join([
      '',
      '--%s' % boundary_id,
      soap_headers,
      str(soap_xml),
      '--%s' % boundary_id,
      attachment_headers,
      data,
      '--%s--' % boundary_id
    ])

    # Stuff everything into a request object
    headers = suds_method.client.options.headers.copy()
    headers.update(request_headers)
    request = Request(suds_method.client.options.location, request_text)
    request.headers = headers
    # Send the request
    response = suds_method.client.options.transport.send(request)
    return response

