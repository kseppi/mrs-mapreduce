# Mrs
# Copyright 2008 Brigham Young University
#
# This file is part of Mrs.
#
# Mrs is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# Mrs is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# Mrs.  If not, see <http://www.gnu.org/licenses/>.
#
# Inquiries regarding any further use of the Materials contained on this site,
# please contact the Copyright Licensing Office, Brigham Young University,
# 3760 HBLL, Provo, UT 84602, (801) 422-9339 or 422-3821, e-mail
# copyright@byu.edu.

def mockparallel_main(registry, user_run, user_setup, args, opts):
    """Run Mrs Mockparallel

    This creates all of the tasks that are used in the normal parallel
    implementation, but it executes them in serial.  This can make debugging a
    little easier.
    """

    raise NotImplementedError("The mockparallel implementation is temporarily"
            " broken.  Sorry.")

    from job import Job
    from util import try_makedirs

    # Set up shared directory
    try_makedirs(opts.mrs_shared)

    # create job thread:
    job = Job(registry, user_run, user_setup, args, opts)
    job.start()

    mockparallel(job)

    return 0


# TODO: rewrite Serial implementation to use job and to be more general
def serial(job):
    """Run a MapReduce job in serial."""
    job = self.job
    job.start()

    # Run Tasks:
    while not job.done():
        # do stuff here

        job.check_done()

    job.join()


def mockparallel(job):
    """MapReduce execution on POSIX shared storage, such as NFS
    
    Specify a directory located in shared storage which can be used as scratch
    space.

    Note that progress times often seem wrong in mockparallel.  The reason is
    that most of the execution time is in I/O, and mockparallel tries to load
    the input for all reduce tasks before doing the first reduce task.
    """

    while not job.done():
        task = job.schedule()
        # FIXME (busy loop):
        if task is None:
            continue
        print 'got a task'
        task.active()
        task.run()
        task.finished()
        job.check_done()

    job.join()

# vim: et sw=4 sts=4
