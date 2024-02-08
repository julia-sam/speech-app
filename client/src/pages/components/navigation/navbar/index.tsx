import React from "react";
import Link from "next/link";

const Navbar = () => {
  return (
    <>
      <div className="w-full h-20 bg-gray-900 sticky top-0">
        <div className="container mx-auto px-4 h-full">
          <div className="flex justify-between items-center h-full">
            <ul className="hidden md:flex gap-x-6 text-white">
              <li>
                <Link href="/audio_analysis">
                  <p>Audio Analysis</p>
                </Link>
              </li>
              <li>
                <Link href="/pronunciation_practice">
                  <p>Practice and Compare</p>
                </Link>
              </li>
              <li>
                <Link href="#">
                  <p>Linguistic Insights</p>
                </Link>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </>
  );
};

export default Navbar;